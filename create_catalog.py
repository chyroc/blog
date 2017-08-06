import os
import datetime
import json

import requests


def get_issues_from_github():
    issues_url = 'https://api.github.com/repos/Chyroc/blog/issues'
    r = requests.get(issues_url)
    if not r.ok:
        raise Exception('get issues error')

    return r.json()


def filter_issues(issues):
    issues = sorted(issues, key=lambda x: x['updated_at'], reverse=True)
    return list(filter(lambda x: x['state'] == 'open' and 'issues' in x['html_url'], issues))


def format_md(issues):
    line_dict = {}
    for issue in issues:
        labels = ', '.join([gen_label_md(i['name']) for i in issue.get('labels', '')])

        updated_at = datetime.datetime.strptime(issue['updated_at'], '%Y-%m-%dT%H:%M:%SZ')
        updated_at = updated_at + datetime.timedelta(hours=8)
        updated_at_key = '{}-{}-{}'.format(updated_at.year, updated_at.month, updated_at.day)

        line = '[{}]({}) {}'.format(issue['title'], issue['html_url'], labels)

        if updated_at_key in line_dict:
            line_dict[updated_at_key].append(line)
        else:
            line_dict[updated_at_key] = [line]

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


def save_metadata(issues, save=True):
    metadata = [{
        'number': issue['number'],
        'title': issue['title'],
        'html_url': issue['html_url'],
        'labels': [i['name'] for i in issue['labels']],
        'created_at': issue['created_at'],
        'updated_at': issue['updated_at']
    } for issue in issues]

    if save:
        with open('.metadata.json', 'w', encoding='utf-8') as f:
            json.dump(metadata, f)

    return metadata


def get_metadata():
    with open('.metadata.json', encoding='utf-8') as f:
        metadata = json.load(f)
    return metadata


def diff_metadata(old, new):
    old_dict = {i['number']: i for i in old}
    new_dict = {i['number']: i for i in new}
    msg = []

    both_num = []

    # 增加
    old_num = old_dict.keys()
    for i in new:
        if i['number'] not in old_num:
            msg.append('add [{}]({})'.format(i['title'], i['html_url']))
        else:
            both_num.append(i['number'])

    # 删除
    new_num = new_dict.keys()
    for i in old:
        if i['number'] not in new_num:
            msg.append('delete [{}]({})'.format(i['title'], i['html_url']))

    # 名字改变
    for i in both_num:
        if old_dict[i]['title'] != new_dict[i]['title']:
            msg.append('change [{}]({})\'s title to {}'.format(old_dict[i]['title'], old_dict[i]['html_url'],
                                                               new_dict[i]['title']))

    # label改变
    for i in both_num:
        if old_dict[i]['labels'] != new_dict[i]['labels']:
            msg.append(
                'change [{}]({})\'s label [{}] to [{}]'.format(old_dict[i]['title'], old_dict[i]['html_url'],
                                                               ', '.join(old_dict[i]['labels']),
                                                               ', '.join(new_dict[i]['labels'])))

    if len(msg) == 0:
        # 内容改变(update 时间改变)
        for i in both_num:
            if old_dict[i]['updated_at'] != new_dict[i]['updated_at']:
                msg.append('[{}]({}) change some content'.format(old_dict[i]['title'], old_dict[i]['html_url']))

    # 没有任何改变
    return msg


def push_to_github(commit_msg):
    os.system('git commit -a -m "{}" && git push'.format('\n'.join(commit_msg)))


def main():
    issues = filter_issues(get_issues_from_github())

    issues_old = get_metadata()
    issues_new = save_metadata(issues, True)

    commit_msg = diff_metadata(issues_old, issues_new)

    md = format_md(issues)

    write_md_to_readme(md)

    push_to_github(commit_msg)


if __name__ == '__main__':
    main()
