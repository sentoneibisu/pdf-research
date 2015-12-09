import glob
import subprocess

pdf_list = glob.glob('*.pdf')
for pdf in pdf_list:
    pdf = pdf.replace('(','\(')
    pdf = pdf.replace(')','\)')
    output_file = pdf[:-4] + '_uncompressed'
    cmd = 'pdftk %s output %s uncompress' % (pdf,output_file)
    ret_code = subprocess.call(['pdftk',pdf,'output',output_file,'uncompress'])
    if ret_code:
        print '[*] Error: %s' % cmd
    else:
        print '[*] Success: %s' % cmd
