import concurrent.futures, urllib.request,sys
from pathlib import Path
from pypdf import PdfReader
sys.stdout.reconfigure(encoding='utf-8')
out=Path(__file__).parent
urls={
'fast':'https://www.ijcai.org/proceedings/2025/0628.pdf',
'focus':'https://proceedings.neurips.cc/paper_files/paper/2025/file/395409679270591fd2a70abc694cf5a1-Paper-Conference.pdf',
'phpfl':'https://proceedings.neurips.cc/paper_files/paper/2025/file/dcc0ac74ac8b95dc1939804acce0317d-Paper-Conference.pdf',
'masfl':'https://raw.githubusercontent.com/mlresearch/v267/main/assets/yan25f/yan25f.pdf',
'fedrenyi':'https://raw.githubusercontent.com/mlresearch/v286/main/assets/ma25a/ma25a.pdf',
'fedback':'https://raw.githubusercontent.com/mlresearch/v283/main/assets/cummins25a/cummins25a.pdf',
'nonaligned':'https://cis.temple.edu/~jiewu/research/publications/Publication_files/iwqos2025-final14.pdf',
'darn':'https://www.vldb.org/pvldb/vol18/p3531-miao.pdf',
'defedavg':'https://arxiv.org/pdf/2402.11198',
}
def read(item):
 key,url=item
 try:
  with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'AcademicLiteratureReview/1.0'}),timeout=35) as r:data=r.read()
  if not data.startswith(b'%PDF'):return key+' not PDF'
  f=out/(key+'.pdf');f.write_bytes(data)
  reader=PdfReader(f)
  text='\n'.join(f'\n=== PAGE {i+1} ===\n'+(p.extract_text() or '') for i,p in enumerate(reader.pages))
  (out/(key+'.txt')).write_text(text,encoding='utf-8')
  return key+' '+str(len(reader.pages))+' pages '+str(len(text))+' characters'
 except Exception as e:return key+' '+str(e)
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
 for msg in pool.map(read,urls.items()):print(msg,flush=True)
