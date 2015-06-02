import os
import re

class CloudScapeModules(object):
    """
    Construct an object consisting of all modules required to run each
    CloudScape component. Scans the CloudScape source code for import
    statements and constructs a dictionary of imported modules.
    """
    def construct(self):
        
        # Store all imported modules
        imp_def  = {}
        from_def = {}
        
        for r,d,f in os.walk('../python/cloudscape'):
            for _f in f:
                
                # Comment block marker
                is_comment = False
                
                # If scanning a regular Python file
                if re.match(r'^.*\.py$', _f):
                    file = '%s/%s' % (r, _f)
                    contents = open(file, 'r').read()

                    # If processing a multi-line import statement                    
                    is_from  = False
                    from_mod = None
                    is_imp   = False
                
                    # Process each file line
                    for l in contents.splitlines():
                        
                        # If processing a single line comment block
                        if re.match(r'^[ ]*"""[^"]*"""$', l):
                            continue
                        
                        # If processing a comment block
                        if is_comment:
                            if '"""' in l:
                                is_comment = False
                            continue    
                    
                        # If processing the opening of a comment block
                        if '"""' in l:
                            is_comment = True
                            continue
                    
                        # If processing a single line comment
                        if re.match(r'^[ ]*#.*$', l):
                            continue
                        
                        # If processing a multi-line import statement
                        if is_imp:
                            for i in l.strip().split(','):
                                is_imp = False if not '\\' in i else True
                        
                                if i.strip():
                                    if not i in imp_def:
                                        as_name = False
                                        m_name  = i.strip()
                                        if ' as ' in i:
                                            i_name  = re.compile(r'(^[^ ]*)[ ]*as[ ]*.*$').sub(r'\g<1>', i)
                                            as_name = re.compile(r'^[^ ]*[ ]*as[ ]*(.*$)').sub(r'\g<1>', i)
                                        if i != '\\':
                                            imp_def[i_name.replace('(', '').replace(')', '')] = as_name
                            continue
                        
                        # If processing a multi-line from statement
                        if is_from:
                            for f in l.strip().split(','):
                                is_from = False if not '\\' in f else True
                                
                                if not f in from_def[from_mod]:
                                    as_name  = False
                                    obj_name = f.strip()
                                    if ' as ' in f:
                                        obj_name = re.compile(r'(^[^ ]*)[ ]*as[ ]*.*$').sub(r'\g<1>', f)
                                        as_name  = re.compile(r'^[^ ]*[ ]*as[ ]*(.*$)').sub(r'\g<1>', f)
                                    if obj_name != '\\':
                                        from_def[from_mod][obj_name.replace('(', '').replace(')', '')] = as_name
                            continue
                        
                        # Look for either entire module or module object imports
                        imp_match = re.match(r'^import[ ]*.*$', l)
                        from_match = re.match(r'^from[ ]*.*$', l)
                        if imp_match or from_match:
                            
                            # If importing entire module(s)
                            if imp_match:
                                imp_mods = re.compile(r'^import[ ]*(.*$)').sub(r'\g<1>', l)
                                for m in imp_mods.split(','):
                                    
                                    # If continuing import statements on the next line
                                    if '\\' in m:
                                        is_imp = True
                                    
                                    if m.strip():
                                        if not m in imp_def:
                                            as_name = False
                                            m_name  = m.strip()
                                            if ' as ' in m:
                                                m_name  = re.compile(r'(^[^ ]*)[ ]*as[ ]*.*$').sub(r'\g<1>', m)
                                                as_name = re.compile(r'^[^ ]*[ ]*as[ ]*(.*$)').sub(r'\g<1>', m)
                                            imp_def[m_name.replace('(', '').replace(')', '')] = as_name
                                
                            # If importing specific objects from module(s)
                            if from_match:
                                from_regex = re.compile(r'^from[ ]*([^ ]*)[ ]*import[ ]*(.*$)')
                                from_mod   = from_regex.sub(r'\g<1>', l)
                                from_objs  = from_regex.sub(r'\g<2>', l)
                                
                                if not from_mod in from_def:
                                    from_def[from_mod] = {}
                                    
                                # Get each object being imported from the module
                                for _obj in from_objs.split(','):
                                    obj = _obj.strip()
                                    if not obj:
                                        continue
                                    
                                    # If continuing import statements on the next line
                                    if '\\' in obj:
                                        is_from = True
                                    
                                    if not obj in from_def[from_mod]:
                                        as_name  = False
                                        obj_name = obj.strip()
                                        if ' as ' in obj:
                                            obj_name = re.compile(r'(^[^ ]*)[ ]*as[ ]*.*$').sub(r'\g<1>', obj)
                                            as_name  = re.compile(r'^[^ ]*[ ]*as[ ]*(.*$)').sub(r'\g<1>', obj)
                                        if obj_name != '\\':
                                            from_def[from_mod][obj_name.replace('(', '').replace(')', '')] = as_name
    
        # Set the required imports objects
        return { 'import': imp_def, 'from': from_def }