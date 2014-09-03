import sys
import json
import base64

# Django Libraries
from django.conf import settings
from django.template.loader import render_to_string

# CloudScape Libraries
from cloudscape.common.utils import valid, invalid
from cloudscape.common.utils import JSONTemplate
from cloudscape.engine.api.app.formula.models import DBFormulaDetails, DBFormulaTemplates

class EditorGet:
    """
    Retrieve all formula contents, including the manifest and any templates, required to render
    a formula editor page.
    """
    def __init__(self, parent):
        self.api = parent

        # Target formula
        self.formula = self.api.acl.target_object()

    # Get the formula JSON manifest and template files
    def launch(self):
        
        # Construct a list of authorized formulas
        auth_formulas = self.api.acl.authorized_objects('formula', 'formula/get')

        # Make sure the formula exists and is accessible
        if not self.formula in auth_formulas.ids:
            return invalid(self.api.log.error('Requested formula <%s> not found or access denied' % self.formula))

        # Get the formula details
        formula_details = auth_formulas.extract(self.formula)
        
        # Get the formula templates
        formula_templates = {}
        for template_row in DBFormulaTemplates.objects.filter(formula=self.formula).values():
            formula_templates[template_row['template_name']] = template_row['template_file']

        # Encode the manifest
        formula_details['manifest']  = base64.encodestring(json.dumps(formula_details['manifest']))
        
        # Set the templates
        formula_details['templates'] = formula_templates

        # Return the response
        return valid(json.dumps(formula_details))

class EditorOpen:
    """
    Open an instance of a formula for editing, create a lock to prevent this formula from being
    changed by other users.
    """
    def __init__(self, parent):
        self.api = parent
        
        # Target formula
        self.formula = self.api.acl.target_object()

    # Try to open ta formula for editing
    def launch(self):
    
        # Construct a list of authorized formulas
        auth_formulas = self.api.acl.authorized_objects('formula', 'formula/get')

        # Make sure the formula exists and is accessible
        if not self.formula in auth_formulas.ids:
            return invalid(self.api.log.error('Requested formula <%s> not found or access denied' % self.formula))
        
        # Get the formula details row
        formula_details = auth_formulas.extract(self.formula)
        
        # Check if the formula is locked
        if formula_details['locked'] == True:
            self.api.log.info('Formula <%s> already checked out by user <%s>' % (self.formula, formula_details['locked_by']))
            
            # If the formula is checked out by the current user
            if formula_details['locked_by'] == self.api.user:
                self.api.log.info('Formula checkout request OK, requestor <%s> is the same as the locking user <%s>' % (self.api.user, formula_details['locked_by']))
                return valid('Formula already checked out by the current user')
            else:
                return invalid(self.api.log.error('Could not open formula <%s> for editing, already checked out by <%s>' % (self.formula, formula_details['locked_by'])))
    
        # Set the locking user
        locked_by = self.api.user
        
        # Lock the formula for editing
        self.api.log.info('Checkout out formula <%s> for editing by user <%s>' % (self.formula, locked_by))
        try:
            DBFormulaDetails.objects.filter(uuid=self.formula).update(
                locked    = True,
                locked_by = self.api.user
            )
            return valid('Successfully checked out formula for editing')
            
        # Failed to check out the formula
        except Exception as e:
            return invalid(self.api.log.error('Failed to check out formula for editing with error: %s' % e))


class EditorClose:
    """
    Close a formula and remove the editing lock.
    """
    def __init__(self, parent):
        self.api = parent

        # Target formula
        self.formula = self.api.acl.target_object()

    # Try to check in a formula
    def launch(self):
    
        # Construct a list of authorized formulas
        auth_formulas = self.api.acl.authorized_objects('formula', 'formula/get')

        # Make sure the formula exists and is accessible
        if not self.formula in auth_formulas.ids:
            return invalid(self.api.log.error('Requested formula <%s> not found or access denied' % self.formula))
        
        # Get the formula details row
        formula_details = auth_formulas.extract(self.formula)
        
        # Check if the formula is already checked out
        if formula_details['locked'] == False:
            return invalid(self.api.log.error('Could not check in formula <%s>, already checked in' % self.formula))
        
        # Lock the formula for editing
        self.api.log.info('Check in formula <%s> by user <%s>' % (self.formula, self.api.user))
        try:
            DBFormulaDetails.objects.filter(uuid=self.formula).update(
                locked    = False,
                locked_by = None
            )
            return valid('Successfully checked in formula')
            
        # Failed to check out the formula
        except Exception as e:
            return invalid(self.api.log.error('Failed to check in formula with error: %s' % e))

class EditorValidate:
    """
    Validate a formula manifest and template contents prior to saving.
    """
    def __init__(self, parent):
        self.api = parent

        # Target formula
        self.formula = self.api.acl.target_object()

    # Validate the supplied editor contents
    def launch(self):
        self.api.log.info('Running formula editor contents validation')
        
        # Required templates
        required_templates = []
        
        # Make sure all the required templates are set
        for required_template in required_templates:
            if not required_template in self.api.data['formula_templates']:
                return invalid(self.api.log.error('Missing required template \'%s\' in request data' % required_template))
        
        # Decode the base64 versions of the formula manifest and templates
        try:
            self.api.log.info('Decoding formula <%s> manifest' % self.formula)
            manifest  = base64.decodestring(self.api.data['manifest'])
            templates = {}
            if 'templates' in self.api.data:
                for t_name, t_content in self.api.data['templates'].iteritems():
                    self.api.log.info('Validating formula <%s> template <%s>' % (self.formula, t_name))
                    if not t_content == 'delete':
                        templates[t_name] = base64.decodestring(self.api.data['templates'][t_name])
                    else:
                        templates[t_name] = t_content

        # Objects not base64 encoded
        except Exception as e:
            return invalid(self.api.log.error('An error occured when Base64 decoding formula objects during validation: %s' % e))

        # Validate the formula JSON
        json_err = JSONTemplate(json.load(open(settings.FORMULA_TEMPLATE, 'r'))).validate(json.loads(manifest))
        if json_err:
            return invalid(self.api.log.error(json_err))
        return valid('Successfully validated formula editor contents')

class EditorSave:
    """
    Save any changes to the formula manifest or template contents.
    """
    def __init__(self, parent):
        self.api     = parent
        
        # Target formula
        self.formula = self.api.acl.target_object()
        
    # Save the new formula contents
    def launch(self):
        
        # Validate the content first
        ev_status = self.api.util.EditorValidate.launch()
        if not ev_status['valid']:
            return ev_status
        
        # Save the formula manifest to the database
        try:
            DBFormulaDetails.objects.filter(uuid=self.formula).update(
                manifest = base64.decodestring(self.api.data['manifest'])
            )
            self.api.log.info('Updated manifest for formula <%s>' % self.formula)
        except Exception as e:
            return invalid(self.api.log.error('An error occured when updating the manifest for formula <%s>: %s' % (self.formula, str(e))))
        
        # Save the templates to the database
        if 'templates' in self.api.data:
            for name, encoded in self.api.data['templates'].iteritems():
                
                # New Template
                if not DBFormulaTemplates.objects.filter(formula=self.formula).filter(template_name=name).count():
                    try:
                        DBFormulaTemplates(
                            formula       = DBFormulaDetails.objects.filter(uuid=self.formula).get(),
                            template_name = name,
                            template_file = encoded,
                            size          = sys.getsizeof(encoded)
                        ).save()
                        
                        # Return a socket proxy message
                        self.api.socket.loading('Saving new template <%s>' % name)
                        
                        # Log creation of the new template
                        self.api.log.info('Created formula <%s> template <%s>' % (self.formula, name))
                    
                    # Critical error when creating new template
                    except Exception as e:
                        return invalid(self.api.log.error('An error occured when creating template <%s> source code: %s' % (name, e)))
                    
                # Delete Template
                elif encoded == 'delete':
                    try:
                        
                        # Only delete if it already exists
                        if DBFormulaTemplates.objects.filter(formula=self.formula).filter(template_name=name).count():
                            DBFormulaTemplates.objects.filter(formula=self.formula).filter(template_name=name).delete()
                            
                            # Return a socket proxy message
                            self.api.socket.loading('Deleting template <%s>' % name)
                            
                            # Log deletion of the template
                            self.api.log.info('Deleted formula <%s> template <%s>' % (self.formula, name))
                    
                    # Critical error when deleting template
                    except Exception as e:
                        return invalid(self.api.log.error('An error occured when deleting template <%s> source code: %s' % (name, e)))
                    
                # Update Template
                else:
                    try:
                        DBFormulaTemplates.objects.filter(formula=self.formula).filter(template_name=name).update(
                            template_file = encoded,
                            size          = sys.getsizeof(encoded)
                        )
                        
                        # Return a socket proxy message
                        self.api.socket.loading('Saving template <%s>' % name)
                        
                        # Log update of the template
                        self.api.log.info('Updated formula <%s> template <%s>' % (self.formula, name))
                        
                    # Critical error when updating template
                    except Exception as e:
                        return invalid(self.api.log.error('An error occured when updating template <%s> source code: %s' % (name, e)))
        
        # All changes saved
        self.api.socket.loading('All template changes saved...')
        return valid('All changes to the formula have been saved')