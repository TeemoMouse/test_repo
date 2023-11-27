import argparse as ap
import opencc as cc
import os, yaml, shutil, time
import logging, subprocess, traceback
from logging.handlers import RotatingFileHandler
import logger_format_settting as LFS
import modify_rela_html as MRH
import chatgpt_api as chatgpt

# Initialize
# Logging format
LFS.initialize()

# Current time
CURR_TIME = int(time.time())
CURR_STRF = time.strftime("%Y-%m-%d %H:%M:%S")

# Global variable
debug_logger = None
error_logger = logging.getLogger('error')   # Error logger

# Make help info and set arguments.
def make_parser():
    # Parse arguments
    parser = ap.ArgumentParser(description='Hexo Web Builder!')

    group1 = parser.add_mutually_exclusive_group()
    group1.add_argument('-s', '--server', action='store_true', default = False, help='open local server')
    group1.add_argument('-p', '--push', action='store_true', default = False, help='push to GitHub')

    parser.add_argument('-c', '--chatgpt', type=str, metavar='keyword', nargs='+', help='open chatgpt mode')
    parser.add_argument('-d', '--debug', action='store_true', default = False, help='open debug mode')
    parser.add_argument('-r', '--rebuild', action='store_true', default = False,help='re-build project')
    # Choose the setting file from ./customize/input_settings/
    parser.add_argument('-n', '--new', action='store_true', default = False, help='Create a new project according to setting file.')
    # Choose the setting file from ./saved_set/
    parser.add_argument('saved_set_file', type=str, help='use saved setting file which been created before.')
    return parser

# Make debug logger
def make_debug_logger():
    logger = logging.getLogger('debug')
    return logger

# Write debug log
def write_log(logger, content=None, ty='info', process_name='builder.py'):
    if content != None:
        if type(content) == bytes:
            try:
                content = content.decode('utf-8')
            except:
                # 'big5' is a trash encoding.💣😭
                content = content.decode('big5')
        content = content.strip()
    
    if logger != None:
        if ty == 'warning':
            for line in content.split('\n'):
                if line != '':
                    logger.warning(line.strip(), extra={'process_name': process_name})
                    print('[{}] Warning: {}'.format(logger.name, line.strip()))
        elif ty == 'debug':
            for line in content.split('\n'):
                if line != '':    
                    logger.debug(line.strip(), extra={'process_name': process_name})
                    print('[{}] Debug: {}'.format(logger.name, line.strip()))
        elif ty == 'error':
            for line in content.split('\n'):
                if line != '':    
                    logger.error(line.strip(), extra={'process_name': process_name})
                    print('[{}] Error: {}'.format(logger.name, line.strip()))
        else:   # info
            for line in content.split('\n'):
                if line != '':    
                    logger.info(line.strip(), extra={'process_name': process_name})
                    print('[{}] Info: {}'.format(logger.name, line.strip()))

# Build new Hexo project
def new_Hexo_project(replace: bool, project_name: str):
    global debug_logger, error_logger
    if replace:
        if os.path.exists(r'./projects/{}'.format(project_name)):
            # It may use `sudo`
            shutil.rmtree(r'./projects/{}'.format(project_name))
    if os.path.exists(r'./projects/{}'.format(project_name)):
        return
    my_process = subprocess.Popen([r"newHexo.bat", project_name], stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True, encoding='utf-8')
    output, error = my_process.communicate()
    #os.system(r'newHexo.bat {}'.format(project_name))

    # Write log
    write_log(debug_logger, output, 'debug', 'newHexo.bat')
    if error:
        write_log(error_logger, error, 'error', 'newHexo.bat')
    
# Copy origin theme to new theme
def copy_origin_theme(project_name: str, theme_name: str, new_theme_name: str):
    global debug_logger, error_logger
    
    my_process = subprocess.Popen([r"copyOriginTheme.bat", project_name, theme_name, new_theme_name], stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
    output, error = my_process.communicate()
    #os.system(r'copyOriginTheme.bat {} {} {}'.format(project_name, theme_name, new_theme_name))

    # Write log
    write_log(debug_logger, output, 'debug', 'copyOriginTheme.bat')
    if error:
        write_log(error_logger, error, 'error', 'copyOriginTheme.bat')

# Run theme's origin setting
def run_theme_origin_setting(project_name: str, theme_name: str):
    global debug_logger, error_logger

    # Load theme's commands
    commands = []
    with open(r'./all_origin_settings/{}/commands.txt'.format(theme_name), 'r', encoding='utf-8') as f:
        commands = f.read().split('\n')

    # Run theme's setting commands
    with open(r'auto_install.bat'.format(project_name), '+w', encoding='utf-8') as f:
        f.write('@ECHO OFF\nchcp 65001\ncd projects\\{}\\\n'.format(project_name, theme_name))
        for command in commands:
            if command != '':
                f.write(command + '\n')
    
    my_process = subprocess.Popen(['auto_install.bat'], stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True, encoding='utf-8')
    output, error = my_process.communicate()
    #os.system('call "./projects/{}/auto_install.bat"'.format(project_name))

    # Write log
    write_log(debug_logger, output, 'debug', r"{}:auto_install.bat".format(project_name))
    if error:
        write_log(error_logger, error, 'error', r"{}:auto_install.bat".format(project_name))

    # Load default config
    config = {}
    with open("DEFAULT_CONFIG.yml", "r") as f:
        config = yaml.safe_load(f)

    # Modify config data
    with open(r'./all_origin_settings/{}/config.yml'.format(theme_name), 'r', encoding='utf-8') as f:
        yaml_data = yaml.safe_load(f)
        for yaml_key in yaml_data:
            config[yaml_key] = yaml_data[yaml_key]
    yaml.dump(config, open(r'./projects/{}/_config.yml'.format(project_name), 'w', encoding='utf-8'), default_flow_style=False)

# Use customized config to modify project's config
def modify_project_config(project_name: str, user_config_path: str, new_theme_name: str):
    config = {}
    with open(r'./DEFAULT_CONFIG.yml'.format(project_name), 'r', encoding='utf-8') as f:
        with open(r'./customize/project_configs/{}'.format(user_config_path), 'r', encoding='utf-8') as f2:
            yaml_data = yaml.safe_load(f2)
            if yaml_data == None:
                yaml_data = {}
            yaml_data['theme'] = new_theme_name   # Change theme name
            if yaml_data == None:
                return
            config = yaml.safe_load(f)
            for yaml_key in yaml_data:
                config[yaml_key] = yaml_data[yaml_key]
    yaml.dump(config, open(r'./projects/{}/_config.yml'.format(project_name), 'w', encoding='utf-8'), default_flow_style=False)

# Use customized config to modify theme's config
def modify_theme_config(project_name: str, new_theme_name: str, user_config_path: str):
    config = {}
    with open(r'./projects/{}/themes/{}/_config.yml'.format(project_name, new_theme_name), 'r', encoding='utf-8') as f:
        with open(r'./customize/theme_configs/{}'.format(user_config_path), 'r', encoding='utf-8') as f2:
            yaml_data = yaml.safe_load(f2)
            if yaml_data == None:
                return
            config = yaml.safe_load(f)
            for yaml_key in yaml_data:
                config[yaml_key] = yaml_data[yaml_key]
    yaml.dump(config, open(r'./projects/{}/themes/{}/_config.yml'.format(project_name, new_theme_name), 'w', encoding='utf-8'), default_flow_style=False)

# Copy selected .md files to project's source/_posts
def add_md_files(project_name: str, md_files_list: list, chatgpt_keywords: list) -> list:
    global debug_logger, error_logger, CURR_TIME, CURR_STRF
    
    # Clear all .md files in source/_posts
    my_process = subprocess.Popen([r"clearMDfile.bat", project_name], stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True, encoding='utf-8')
    output, error = my_process.communicate()
    
    #os.system(r'clearMDfile.bat {}'.format(project_name))

    # Write log
    write_log(debug_logger, output, 'debug', 'clearMDfile.bat')
    if error:
        write_log(error_logger, error, 'error', 'clearMDfile.bat')
    
    # Copy selected .md files to project's source/_posts
    for md_file in md_files_list:
        my_copy_process = subprocess.Popen([r"copyMDfile.bat", project_name, str(md_file)], stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True, encoding='utf-8')
        output, error = my_copy_process.communicate()
        #os.system(r'copyMDfile.bat {} {}'.format(project_name, md_file))
        # Write log
        write_log(debug_logger, output, 'debug', 'copyMDfile.bat')
        if error:
            write_log(error_logger, error, 'error', 'copyMDfile.bat')

    if chatgpt_keywords != None:
        total, count = 3 * len(chatgpt_keywords), 0
        trans = cc.OpenCC('s2tw')
        for keyword in chatgpt_keywords:
            keyword = keyword.strip()
            quetions = chatgpt.read_default_question(keyword)
            mes = []
            
            with open(r'./md/{}_{}.md'.format(keyword, CURR_TIME), '+a', encoding='utf-8') as f:
                f.write('---\n')
                f.write('title: {}\n'.format(keyword))
                f.write('date: {}\n'.format(CURR_STRF))
                f.write('tags: [{}]\n'.format(keyword))
                f.write('---\n\n')
            for question in quetions:
                count += 1
                print("Processing: {}/{}\nQ: {}".format(count, total, question))
                resp = chatgpt.ask_chatgpt(question, mes).encode('utf-8').decode('utf-8')
                resp = trans.convert(resp)
                mes.append(
                    {
                        "role": "assistant",
                        "content": resp,
                    }
                )
                print("A: {}".format(resp))

                with open(r'./md/{}_{}.md'.format(keyword, CURR_TIME), '+a', encoding='utf-8') as f:
                    for line in resp.split('\n')[:-1]:
                        if len(line) > 0:
                            f.write(line + '\n')
            md_files_list.append('{}_{}.md'.format(keyword, CURR_TIME))

            # Copy selected .md files to project's source/_posts
            #os.system(r'copyMDfile.bat {} {}_{}.md'.format(project_name, keyword, curr_time))
            my_copy_process = subprocess.Popen([r"copyMDfile.bat", project_name, '{}_{}.md'.format(keyword, CURR_TIME)], stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True, encoding='utf-8')
            output, error = my_copy_process.communicate()
            # Write log
            write_log(debug_logger, output, 'debug', 'copyMDfile.bat')
            if error:
                write_log(error_logger, error, 'error', 'copyMDfile.bat')
    return [e.encode('utf-8').decode('utf-8') for e in md_files_list]

# Fix relative path in html files
def fix_path(project_name: str, repository_name: str):
    all_html = []
    for p, d, f in os.walk('./projects/{}/public'.format(project_name)):
        for file in f:
            if file.endswith('.html'):
                all_html.append(os.path.join(p, file))

    for ele in all_html:
        MRH.modify_html_relative_path(ele, ele, repository_name)

# Set GitHub username and email
def set_github_config(project_name: str, github_username: str, github_email: str):
    # Set GitHub username and email by script.
    my_process = subprocess.Popen([r"setGithubConfig.bat", project_name, github_username, github_email], stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True, encoding='utf-8')
    output, error = my_process.communicate()

    # Write log
    write_log(debug_logger, output, 'debug', 'setGithubConfig.bat')
    if error:
        write_log(error_logger, error, 'error', 'setGithubConfig.bat')

# Git push to GitHub
def git_push_to_github(project_name: str, branch_name:str,  github_url:str):
    # Git add, commit, remote and push.
    my_process = subprocess.Popen([r"pushProject.bat", project_name, branch_name, github_url], stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True, encoding='utf-8')
    output, error = my_process.communicate()

    # Write log
    write_log(debug_logger, output, 'debug', 'pushProject.bat')
    if error:
        write_log(error_logger, error, 'error', 'pushProject.bat')

# Build website according to config and run server
def build_website(project_name: str, is_run_server: bool):
    global debug_logger, error_logger
    try:
        my_process = subprocess.Popen([r"quick_setting.bat", project_name], stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True, encoding='utf-8')
        output, error = my_process.communicate()
        #os.system(r'quick_test.bat {} {}'.format(project_name, int(is_run_server)))

        # Write log
        write_log(debug_logger, output, 'debug', 'quick_test.bat')
        if error:
            write_log(error_logger, error, 'error', 'quick_test.bat')

        # run server
        if is_run_server:
            os.system(r'run_server.bat {}'.format(project_name))

    except KeyboardInterrupt:
        print('Server closed.')

def save_yml(user_config: dict):
    global CURR_TIME
    # Save user's yaml setting file
    with open(r'./saved_set/{}_{}.yml'.format(user_config['project_name'], CURR_TIME), '+w', encoding='utf-8') as f:
        yaml.dump(user_config, f, default_flow_style=False, allow_unicode=True)

# Main function
if __name__ == '__main__':
    # Parse arguments
    parser = make_parser()
    args = parser.parse_args()

    # Make debug logger
    if args.debug:
        debug_logger = make_debug_logger()
        print('Debug mode opened!')

    # New project
    if args.new:
        # Constant
        SETTING_DEFAULT_PATH = r'./customize/input_settings/'

        try:
            # Load user's yaml setting file
            user_config = {}
            with open(SETTING_DEFAULT_PATH + args.saved_set_file, 'r', encoding='utf-8') as f:
                user_config = yaml.safe_load(f)
            
            # Build oringin Hexo projectand selected theme
            new_Hexo_project(args.rebuild, user_config['project_name'])
            copy_origin_theme(user_config['project_name'], user_config['theme_name'], user_config['new_theme_name'])
            run_theme_origin_setting(user_config['project_name'], user_config['theme_name'])
            
            # According to user's setting file, modify project's config and theme's config
            if user_config['project_config'] != None:
                modify_project_config(user_config['project_name'], user_config['project_config'], user_config['new_theme_name'])
            if user_config['theme_config'] != None:
                modify_theme_config(user_config['project_name'], user_config['new_theme_name'], user_config['theme_config'])
            

            # Add .md files to project's source/_posts
            if args.chatgpt != None and len(args.chatgpt) == 0:
                args.chatgpt = None
            
            if args.chatgpt != None:
                args.chatgpt = list(set(args.chatgpt))

            files = add_md_files(user_config['project_name'], user_config['markdown_files'], args.chatgpt)
            user_config['markdown_files'] = files
            
            # Push to GitHub if -p is True
            if args.push:
                fix_path(user_config['project_name'], user_config['account']['repository'])
                set_github_config(user_config['project_name'], user_config['account']['user_name'], user_config['account']['email'])
                git_push_to_github(user_config['project_name'], user_config['account']['branch'], "git@github.com:{}/{}.git".format(user_config['account']["user_name"], user_config['account']["repository"]))
            save_yml(user_config)

            # Build website and run server
            build_website(user_config['project_name'], args.server)

        except Exception as e:
            write_log(error_logger, traceback.format_exc(), 'error', 'builder.py')
            print('Error! Builder stopped.')
        finally:
            print('Builder stopped.')
    # Update project
    else:
        try:
            pass
        except Exception as e:
            pass