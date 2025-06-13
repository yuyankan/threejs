import base64
from email.message import EmailMessage
from googleapiclient.discovery import build

import tooken_google_api as tga


def send_mail(creds,
              subject='C11 SPC DAILY REPORT', 
              content='Hi,\nPlease find below C11 SPC ALARM DAILY REPORT', 
              image_url_list =['image.jpg'], 
              image_desc_list =['',],
              receivers_list=['caren.kan@ap.averydennison.com']):

    service = build('gmail', 'v1', credentials=creds)

    # ---------------------
    # 2. 构造邮件内容
    # ---------------------
    message = EmailMessage()
    message['To'] = ','.join(receivers_list)
    message['From'] = 'caren.kan@ap.averydennison.com'
    message['Subject'] = subject

    #顺序： 先设纯文本：
    message.set_content(content)
    image_cid = "image001"

    message.add_alternative(f"""
    <html>
    <body>
        <p>Hi,<br>Please find below C11 SPC ALARM DAILY REPORT.</p>
        <img src="cid:{image_cid}" width="1000" stype="max-width:100%; height:auto;">
        <br><br>
        <p>BR.<br>Caren Kan</p>
    </body>
    </html>
    """, subtype='html')

    # 设置 HTML 内容，内嵌图片引用 CID
    # 加载图片并转为 MIME 资源
    image_cid = 'image001'  # 引用用的 cid
    with open(image_url_list[0], 'rb') as img:
        img_read = img.read()
        message.get_payload()[1].add_related(img_read, maintype='image', subtype='jpeg', cid=image_cid)


    # ---------------------
    # 3. 编码并发送
    # ---------------------
    encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

    send_result = service.users().messages().send(
        userId='me',
        body={'raw': encoded_message}
    ).execute()

    print("✅ 邮件已发送，ID:", send_result['id'])

def work(subject='C11 SPC DAILY REPORT',
         content='Hi,\nPlease find below C11 SPC ALARM DAILY REPORT',
         image_url_list =['image.jpg'],
         image_desc_list =['',],
        receivers_list=['caren.kan@ap.averydennison.com']
        ):
    # Gmail API 范围（用于发送邮件）
    SCOPES = ['https://www.googleapis.com/auth/gmail.send']

    # ---------------------
    # 1. 授权 Gmail API
    # ---------------------
    creds = tga.get_token(SCOPES)
    
    send_mail(creds=creds,
              subject=subject, 
              content=content, 
              image_url_list =image_url_list, 
              image_desc_list =image_desc_list,
              receivers_list=receivers_list)

if __name__=='__main__':
    work()
