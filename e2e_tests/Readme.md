# lyrebird e2e test

## 测试 lyrebird（POST）request body

```bash
pip install -e .[dev]
# If you are using zsh you need to escape square brackets or use quotes:
# pip install -e .\[extra\]
# or
# pip install -e ".[extra]"
cd e2e_tests
python -m pytest .
```
