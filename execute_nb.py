from nbclient import NotebookClient
from nbformat import read, write
p='cafelocate/ml/model_training_comprehensive_ahp.ipynb'
nb=read(open(p,'r',encoding='utf-8'),as_version=4)
client=NotebookClient(nb, timeout=600, kernel_name='python3')
try:
    client.execute()
    write(nb, open('cafelocate/ml/model_training_comprehensive_ahp_executed.ipynb','w',encoding='utf-8'))
    print('Executed notebook successfully')
except Exception as e:
    import traceback
    traceback.print_exc()
    print('Notebook execution failed')
