import requests
import datetime


def get_issues_from_github():
    issues_url = 'https://api.github.com/repos/Chyroc/blog/issues'
    r = requests.get(issues_url)
    if not r.ok:
        raise Exception('get issues error')

    return r.json()


def format_md(issues):
    line_dict = {}
    for issue in issues:
        if issue['state'] != 'open':
            continue

        labels = ', '.join([gen_label_md(i['name']) for i in issue.get('labels', '')])

        created_at = datetime.datetime.strptime(issue['created_at'], '%Y-%m-%dT%H:%M:%SZ')
        created_at_key = '{}-{}'.format(created_at.year, created_at.month)

        line = '[{}]({}) {}'.format(issue['title'], issue['html_url'], labels)

        if created_at_key in line_dict:
            line_dict[created_at_key].append(line)
        else:
            line_dict[created_at_key] = [line]

    return line_dict


def gen_label_md(label):
    return '[#{}](https://github.com/Chyroc/blog/issues?q=is:issue+is:open+label:{})'.format(label, label)


def write_line(f, line=None, empty_count=1):
    if line is not None:
        f.write(line)
    for i in range(empty_count):
        f.write('\n')


def write_md_to_readme(md):
    with open('README.md', 'w', encoding='utf-8') as f:
        write_line(f, 'Chyroc Blog')
        write_line(f, '> created by issue', 2)

        for k, vs in md.items():
            write_line(f, '### {}'.format(k))
            for v in vs:
                write_line(f, '- {}'.format(v))

            write_line(f)


if __name__ == '__main__':
    issues = get_issues_from_github()

    md = format_md(issues)

    write_md_to_readme(md)
