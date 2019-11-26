from pathlib import Path
import jinja2
import codecs

here = Path(__file__).parent
demo_project = Path(here) / 'lyrebird_plugin_demo'


def make_plugin_project(project_name, project_dir):
    # Context
    ctx = {
        'project_name': project_name
    }
    # Make project dir
    Path(project_dir).expanduser().absolute().mkdir(parents=True, exist_ok=True)
    # Copy files to target dir
    _cp_dir(ctx, demo_project, project_dir)


def _cp_dir(ctx, _path, target):
    target_dir = Path(target)
    if target_dir.name == '$_plugin_name':
        target = target_dir.parent/ctx['project_name']
    # Make target directory
    Path(target).mkdir(parents=True, exist_ok=True)
    print(f'MKDIR {target}')
    # cp subfile to target dir
    for subfile in Path(_path).iterdir():
        if subfile.is_dir():
            _cp_dir(ctx, subfile, Path(target)/subfile.name)
        elif subfile.is_file():
            _cp_file(ctx, subfile, Path(target)/subfile.name)


def _cp_file(ctx, _path, target):
    print(f'CP file {_path} to {target}')
    if Path(target).suffix in ['.py', '.txt', '.md', '.in', '.js']:
        with codecs.open(_path, 'r', 'utf-8') as f_in, codecs.open(target, 'w', 'utf-8') as f_out:
            in_file_string = f_in.read()
            file_template = jinja2.Template(in_file_string)
            in_file_string = file_template.render(project_name=ctx['project_name'])
            f_out.write(in_file_string)
    else:
        with codecs.open(_path, 'rb') as f_in, codecs.open(target, 'wb') as f_out:
            f_out.write(f_in.read())
