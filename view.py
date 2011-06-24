import settings
import pdb
import os


class VARNA:
    
    @classmethod
    def get_colorMapStyle(self, values):
        if reduce(lambda x,y: x and y, [x < 0 for x in values]):
	    return '-0.001:#C0C0C0,0:#FFFFFF;0.1:#FFFFFF,0.8:#FF8800;1:#FF0000'
	else:
	    return '0:#FFFFFF;0.1:#FFFFFF,0.8:#FF8800;1:#FF0000'
    
    @classmethod
    def cmd(self, sequence, structure, outfile, options={}):
        option_str = ''
	for key in options:
	    val = options[key]
	    if type(val) == list:
		argval = str(val).strip('[]').replace('L', '').replace('u','')
	    else:
		argval = str(val)
	    option_str += '-%s "%s" ' % (key, argval)
	print('java -cp %s  fr.orsay.lri.varna.applications.VARNAcmd -sequenceDBN %s -structureDBN "%s" %s -o %s' %\
		  (settings.VARNA, sequence, structure, option_str, outfile))
	os.popen('java -cp %s  fr.orsay.lri.varna.applications.VARNAcmd -sequenceDBN %s -structureDBN "%s" %s -o %s' %\
		  (settings.VARNA, sequence, structure, option_str, outfile))

    def __init__(self, sequences=[], structures=[]):
        self.sequences = sequences
	self.structures = structures
	self.rows = 1
	self.columns = 1
	self.width = 522
	self.height = 200
	self.annotation_font_size = 9
    
    def get_values(self, att):
        if att == 'structures':
	    return [struct.dbn for struct in self.structures]
        return self.__dict__[att]
    
    def get_frames(self):
        res = -1
        for val in self.__dict__.values():
	    if type(val) == list:
		res = max(res, len(val))
	return res

    def render(self, base_annotations={}, annotation_by_helix=False, helix_function=(lambda x,y:x), overlap_structures=False):
        struct_string = ''
	applet_string = '<applet  code="VARNA.class" codebase="http://varna.lri.fr/bin"\n'
	applet_string += 'archive="VARNA.jar" width="%d" height="%d">\n' % (self.width, self.height)
	frames = self.get_frames()
	if overlap_structures:
	    struct_string += '<param name="structureDBN" value="%s"/>\n' % self.structures[0].dbn
	    bps = self.structures[0].base_pairs()
	    struct_string += '<param name="auxBPs" value="'
	    for i in range(1, len(self.structures)):
		for bp in self.structures[0].base_pairs():
		    if bp not in bps:
			bps.append(bp)
			struct_string += '%s:edge5=s, edge3=h, stericity=cis;'
	    struct_string += '"/>\n'
	base_annotation_string = ''
	if len(base_annotations) > 0:
	    base_annotation_string = '<param name="annotations" value=\n\t"'
	    if annotation_by_helix:
		for helix in self.structures[0].helices():
		    anchor = helix[0][0] + 1 + (helix[-1][0] - helix[0][0])/2 
		    annotation_value = base_annotations.values()[0]
		    for bp in helix:
			if bp in base_annotations:
			    nextval = base_annotations[bp]
			    annotation_value = helix_function(annotation_value, nextval)
		    base_annotation_string += '%s:type=L,anchor=%d,size=%d;\n' % (annotation_value, anchor, self.annotation_font_size)
	    else:
		for bp in base_annotations:
		    base_annotation_string += '%s:type=B,anchor=%d,size=%d;\n' % (base_annotations[bp], bp[0], self.annotation_font_size)	
            base_annotation_string = base_annotation_string.strip() + '"/>\n'
	    applet_string += base_annotation_string
	if self.rows * self.columns != frames:
	    rows = frames
	    columns = 1
	else:
	    rows = self.rows
	    columns = self.columns
	param_string = ''
	param_string += '<param name="rows" value="%d"/>\n' % rows
	param_string += '<param name="columns" value="%d"/>\n' % columns
	for att in self.__dict__:
	    if overlap_structures and att == 'structures':
		param_string += struct_string
	    if type(self.get_values(att)) == list:
		if att == 'structures':
		    name = 'structureDBN'
		elif att == 'sequences':
		    name = 'sequenceDBN'
		else:
		    name = att
		for i, val in enumerate(self.get_values(att)):
		    if frames > 1:
			param_string += '<param name="%s%d" value="%s" />\n' % (name, i+1, val)
		    else:
			param_string += '<param name="%s" value="%s" />\n' % (name, val)
	applet_string += param_string
	applet_string += '</applet>'
	return applet_string

	
	


