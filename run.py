#!/Users/zhaoye/work/github/lyrebird/venv/bin/python3
from lyrebird.manager import main
import multiprocessing


if __name__ == '__main__':
    multiprocessing.freeze_support()
    multiprocessing.set_start_method('spawn')

    main()
