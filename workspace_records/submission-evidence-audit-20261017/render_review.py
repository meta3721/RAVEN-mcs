from pathlib import Path
import pypdfium2 as pdfium
from PIL import Image, ImageDraw

root=Path('C:/Cursor/raven.mcs/TO_OVERLEAF_paper_tmc_r1_clean')
out=Path(__file__).parent
for stem in ['main','supplemental']:
    doc=pdfium.PdfDocument(root/(stem+'.pdf'))
    sheet=Image.new('RGB',(4*340,4*465),'#dddddd')
    draw=ImageDraw.Draw(sheet)
    for i in range(len(doc)):
        page=doc[i]
        bitmap=page.render(scale=.53)
        pic=bitmap.to_pil().convert('RGB')
        x=(i%4)*340+8; y=(i//4)*465+25
        sheet.paste(pic,(x,y)); draw.text((x,y-18),f'{stem} p{i+1}',fill='black')
        bitmap.close(); page.close()
    sheet.save(out/(stem+'-contact.jpg'),quality=91)
    for n in ([8,11,12] if stem=='main' else [7,9,12,14]):
        page=doc[n-1]; bitmap=page.render(scale=1.7)
        bitmap.to_pil().save(out/(stem+'-page-'+str(n)+'.png'))
        bitmap.close();page.close()
    doc.close()
print('Rendered both 14-page PDFs for visual inspection; no manuscript changes.')
