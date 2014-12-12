#!/usr/bin/env python
# encoding: utf-8
"""
sg_barcode.py

Generate a movie barcode style image from versions in a shotgun project

Created by Jack James on 2014-12-09.

"""
import os, sys, urllib, cStringIO, argparse
import numpy
from PIL import Image
from shotgun_api3.shotgun import Shotgun

parser = argparse.ArgumentParser(description='Generate Shotgun project barcode')
parser.add_argument('-o', '--output', help='Output file', required=True)
parser.add_argument('-p', '--projectid', help='Project ID', required=True)
parser.add_argument('-s', '--server', help='Server URL', required=True)
parser.add_argument('--scriptname', help='Script name', required=True)
parser.add_argument('--scriptkey', help='Script key', required=True)

args = vars(parser.parse_args())

BARCODE_SIZE = (2000, 400) # width, height

print("Connecting to Shotgun")
sg = Shotgun(args['server'], args['scriptname'], args['scriptkey'])

versionEntity = 'Version'
project_id = int(args['projectid'])
barcode_path = args['output']

def get_barcode_image(versions, barcode_path):
    if os.path.exists(barcode_path):
        return Image.open(barcode_path)
    barcode = Image.new('RGB', BARCODE_SIZE)
    for i, frameNum in enumerate(numpy.linspace(0, len(versions), BARCODE_SIZE[0])):
        version = versions[int(frameNum)-1]
        try:
            # nb we get the url just prior to the thumbnail so we don't time out and end up with a broken thumb
            versionData = sg.find_one(versionEntity, [['id', "is", version['id']]], ['code', 'image'])
            # http://stackoverflow.com/questions/7391945/how-do-i-read-image-data-from-a-url-in-python
            file = cStringIO.StringIO(urllib.urlopen(versionData['image']).read())
            frame_image = Image.open(file)
            frame_image = frame_image.resize((1, BARCODE_SIZE[1]), Image.ANTIALIAS)
            barcode.paste(frame_image, (i, 0))
        except Exception, e:
            print e
        finally:
            sys.stdout.write('processing [%.2f%%] %s \r' % (frameNum *100. / len(versions), version['code'] ))
            sys.stdout.flush()
    barcode.save(barcode_path)
    return barcode

print("Getting all versions with thumbnails")

version_filters = [
        ['image', 'is_not', None],
        ['project', 'is', {'type':'Project','id':project_id}],
        ]
version_fields = ['id', 'code']
version_order = [{'field_name':'created_at', 'direction':'asc'}]
versions = sg.find(versionEntity, version_filters, version_fields, version_order)
print("Found "+str(len(versions))+" versions")

barcode_image = get_barcode_image(versions, barcode_path)

'''
def demo(video_path, barcode_path):
    barcode_image = get_barcode_image(video_path, barcode_path)
    dominant_image = get_dominant_image(barcode_image)
    img_width = max(barcode_image.size[0], dominant_image.size[0])
    img_height = barcode_image.size[1] + dominant_image.size[1]
    img = Image.new('RGB', (img_width, img_height))
    img.paste(barcode_image, (0,0))
    img.paste(dominant_image, (0,barcode_image.size[1]))
    img.show()
    img.save('%s.all.png' % video_path[:video_path.rfind('.')])
'''

'''def main(argv):
    if len(argv) <= 1:
        print 'Usage: python %s 1.avi [2.mkv 3.wmv ...]' % argv[0]
        return 0

    for video_path in argv[1:]:
        barcode_path = '%s.png' % video_path[:video_path.rfind('.')]
        demo(video_path, barcode_path)

if __name__ == '__main__':
    sys.exit(main(sys.argv))'''
