# lyrebird e2e test
## 测试 lyrebird（POST）request body

```bash
nohup python3 serve.py > /dev/null 2>&1 & 
nohup lyrebird -b > /dev/null 2>&1 & 
python -m pytest .
```
