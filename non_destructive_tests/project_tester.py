from time import sleep
from selenium_helper import CssSelector, XpathSelector
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.encoders import encode_base64
from email.mime.text import MIMEText


def get_project_tester(helper):
    return ProjectTester_v7_2_2(helper)


URL_VIEW_ALL_PROJECTS = 'ControlCenter/view_projects.php?view_all=1'

def email_error(report_name, error_text, screenshot=None):
    msg = MIMEMultipart()
    msg['Subject'] = 'No API ETL: Error in ' + report_name
    msg['To'] = 'richard.a.bramley@uhl-tr.nhs.uk'
    msg['From'] = 'richard.a.bramley@uhl-tr.nhs.uk'

    msg.attach(MIMEText(error_text))

    if screenshot:
        part = MIMEBase('image', 'png')
        part.set_payload(screenshot)
        encode_base64(part)

        part.add_header('Content-Disposition',
                        'attachment; filename="screenshot.png"')

        msg.attach(part)

    s = smtplib.SMTP('smtp.xuhl-tr.nhs.uk')
    s.send_message(msg)
    s.quit()



class ProjectTester_v7_2_2():
    def __init__(self, helper):
        self.helper = helper

    def export_items(self):
        self.helper.get(URL_VIEW_ALL_PROJECTS)

        # sleep(5)

        # email_error(
        #     report_name='Project Tester',
        #     error_text='Hello',
        #     screenshot=self.helper.driver.get_screenshot_as_png(),
        # )

        # for a in self.helper.get_elements(CssSelector('a')):
        #     print(self.helper.get_href(a))

    def run(self):
        self.export_items()
