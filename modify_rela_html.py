import bs4, lxml, os

MY_MAPPING = {
    'link': 'href',
    'a': 'href',
    'img': 'src',
    'script': 'src',
    'div': 'onclick'
}

def modify_html_relative_path(html_path: str, name: str, repository_name: str):
    bs = None
    with open(html_path, 'r', encoding='utf-8') as f:
        bs = bs4.BeautifulSoup(f.read(), 'lxml')
    
    for tag, attr in MY_MAPPING.items():
        for t in bs.find_all(tag):
            if t.get(attr):
                if t.get(attr).startswith('http'):
                    continue
                t[attr] = t.get(attr).replace('/', '/{}/'.format(repository_name), 1)

    with open(name, 'w+', encoding='utf-8') as f:
        f.write(str(bs))

if __name__ == '__main__':
    all_html = []
    all_name = []
    for p, d, f in os.walk('./public'):
        for file in f:
            if file.endswith('.html'):
                all_html.append(os.path.join(p, file))
                all_name.append(file)

    for i in range(len(all_html)):
        print('Read {}'.format(all_name[i].split('.')[0] + str(i) + '.html'))
        modify_html_relative_path(all_html[i], all_name[i].split('.')[0] + str(i) + '.html', 'blog')