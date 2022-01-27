import requests
import re
import shutil
import argparse, os

def download(options):
	"""
	Main download function.
	Receives command-line options and downloads all designated files from a user designated page.
	"""
	fileSize = ""
	outputFolder = options.destFolder if options.destFolder else ""
	referer = options.referer if options.referer else ""
	number = 0
	headers = {
		"Sec-Ch-Ua": "\" Not;A Brand\";v=\"99\", \"Google Chrome\";v=\"97\", \"Chromium\";v=\"97\"",
		"Accept-Encoding": "gzip, deflate",
		"Sec-Ch-Ua-Mobile": "?0",
		"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36",
		"Sec-Ch-Ua-Platform": "\"Windows\"",
		"Accept": "*/*",
		"Sec-Fetch-Site": "cross-site",
		"Sec-Fetch-Mode": "no-cors",
		"Sec-Fetch-Dest": "video",
		"Referer": f"{str(referer)}",
		"Accept-Language": "en-US,en;q=0.9",
		"Range": f"bytes=0-{fileSize}"
	}

	url = options.url
	response = requests.get(url, headers=headers)
	regex = options.regex if (options.regex) else "\"file\":\"https://.*?\.mp3"
	links = re.findall(regex, str(response.content))
	links = [link.replace('"file":"', "") for link in links]

	session = requests.session()
	for number in range(0, len(links)):
		chapterUrl = links[number]
		with session.get(chapterUrl, headers=headers, stream=True) as r:
			fileSize = r.headers['Content-Range'].split("/")[1]

		headers['Range'] = f"bytes=0-{fileSize}"
		filename = chapterUrl.split("/")
		filename = filename[len(filename)-1]

		with session.get(chapterUrl, headers=headers, stream=True) as r:
			with open(os.path.join(outputFolder, filename), "wb") as f:
				shutil.copyfileobj(r.raw,f)


if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='This script receives as input a URL of a page, and downloads all linked streaming files from that page.')
	parser.add_argument('-u','--url', help='URL of page where streaming files are located.',required=True)
	parser.add_argument('-r','--referer', help='"Referer" HTTP header of the site.',required=True)
	parser.add_argument('-x','--regex', help='Possible regex to look for wanted files to download.',required=False)
	parser.add_argument('-d','--destFolder', help='Folder where files will be saved in.',required=False)
	options = parser.parse_args()

	download(options)