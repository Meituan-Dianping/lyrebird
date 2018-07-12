from lyrebird.mock import data_manager
from pathlib import Path
import json
import codecs


def make_test_data():
    current_dir = Path(__file__).parent.parent
    # root
    tmp_dir = current_dir/'tmp'
    if not tmp_dir.exists():
        tmp_dir.mkdir()
    # data root
    repo_dir = tmp_dir/'data'
    if not repo_dir.exists():
        repo_dir.mkdir()
    # data group 1
    group1 = repo_dir/'group1'
    if not group1.exists():
        group1.mkdir()
    conf = {'test_key':'test_value'}
    with codecs.open(str(group1/'conf.json'), 'w', 'utf-8') as f:
        f.write(json.dumps(conf, indent=4))
    for i in range(5):
        data_dir = group1/f'data{i}'
        if not data_dir.exists():
            data_dir.mkdir()
        request = {
            "url": "http://www.baidu.com"
        }
        with codecs.open(str(data_dir/'request.json'), 'w', 'utf-8') as f:
            f.write(json.dumps(request, indent=4))
        response = {
            "code": 200
        }
        with codecs.open(str(data_dir/'response.json'), 'w', 'utf-8') as f:
            f.write(json.dumps(response, indent=4))
    # data group 2
    group2 = repo_dir/'group2'
    if not group2.exists():
        group2.mkdir()

def test_create_group():

    make_test_data()
    
    project_dir = Path(__file__).parent.parent
    repo_dir = project_dir/'tmp'/'data'
    repo = data_manager.get_repo(str(repo_dir))
    repo.load()
    print(repo, repo.groups)
