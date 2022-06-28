import os
import requests  # pip install requests #to sent GET requests
from bs4 import BeautifulSoup  # pip install bs4 #to parse html(getting data out from html, xml or other markup languages)
import shutil
import smtplib
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

# user can input a search keyword and the count of images required
# download images from google search image
Google_Image = 'https://www.google.com/search?site=&tbm=isch&source=hp&biw=1873&bih=990&'

# The User-Agent request header contains a characteristic string
# that allows the network protocol peers to identify the application type,
# operating system, and software version of the requesting software user agent.
# needed for google search
u_agnt = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
    'Accept-Encoding': 'none',
    'Accept-Language': 'en-US,en;q=0.8',
    'Connection': 'keep-alive',
}  # write: 'my user agent' in browser to get your browser user agent details

Image_Folder = ''


def main():
    download_images()
    shutil.make_archive(Image_Folder, 'zip', Image_Folder)
    start_mail()



def download_images():
    global Image_Folder
    data = input('Enter your search keyword: ')
    Image_Folder= data
    if not os.path.exists(Image_Folder):
        os.mkdir(Image_Folder)
    num_images = int(input('Enter the number of images you want: '))
    print('Searching Images...')

    search_url = Google_Image + 'q=' + data  # 'q=' because its a query

    # request url, without u_agnt the permission gets denied
    response = requests.get(search_url, headers=u_agnt)
    html = response.text  # To get actual result i.e. to read the html data in text mode

    # find all img where class='rg_i Q4LuWd'
    b_soup = BeautifulSoup(html, 'html.parser')  # html.parser is used to parse/extract features from HTML files
    results = b_soup.findAll('img', {'class': 'rg_i Q4LuWd'})

    # allow to continue the loop in case query fails for non-data-src attributes
    count = 0
    image_links = []
    for res in results:
        try:
            link = res['data-src']
            image_links.append(link)
            count = count + 1
            if (count >= num_images):
                break

        except KeyError:
            continue

    print(f'Found {len(image_links)} images')
    print('Start downloading...')

    for i, image_link in enumerate(image_links):
        # open each image link and save the file
        response = requests.get(image_link)
        image_name = Image_Folder + '/' + data + str(i + 1) + '.jpg'
        with open(image_name, 'wb') as file:
            file.write(response.content)

    print('Download Completed!')


def start_mail():
    mail_content = '''Hello,
    Here are your requested Images
    Thank You for using our service
    '''
    # The mail addresses and password
    sender_address = 'pandeyprashant0311@gmail.com'
    sender_pass = '********'
    receiver_address = 'khuships2001@gmail.com'
    # Setup the MIME
    message = MIMEMultipart()
    message['From'] = sender_address
    message['To'] = receiver_address
    message['Subject'] = 'Requested Images'
    # The subject line
    # The body and the attachments for the mail
    message.attach(MIMEText(mail_content, 'plain'))
    attach_file_name = Image_Folder+'.zip'
    with open(attach_file_name,"rb") as attachment:
        payload = MIMEBase("application", "octet-stream")
        payload.set_payload(attachment.read())

    encoders.encode_base64(payload)  # encode the attachment
    # add payload header with filename
    payload.add_header('Content-Disposition', f'attachment; filename={attach_file_name}',)
    message.attach(payload)
    # Create SMTP session for sending the mail
    session = smtplib.SMTP('smtp.gmail.com', 587)  # use gmail with port
    session.starttls()  # enable security
    session.login(sender_address, sender_pass)  # login with mail_id and password
    text = message.as_string()
    session.sendmail(sender_address, receiver_address, text)
    session.quit()
    print('Mail Sent')


if __name__ == '__main__':
    main()
