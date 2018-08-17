lense.import('tools.manifests', function() { 
	var self = this;
	
	// Manifest editor
	var editor;
	
	/**
	 * Manifest Compile Callback
	 */
	lense.register.callback('compileManifest', function(data) {
		$('#manifests-debug').text(JSON.stringify(JSON.parse(data), undefined, 2));
	});
	
	/**
	 * Manifest Execute Callback
	 */
	lense.register.callback('executeManifest', function(data) {
		$('#manifests-debug').text(JSON.stringify(data, undefined, 2));
	});
	
	/**
	 * Initialize LenseTools Manifests
	 * @constructor
	 */
	this.__init__ = function() {
		$(document).ready(function() {
			
			// Bind events
			self.bind();
			
			// Setup manifest editor
			self.setupEditor();
		});
	}
	
	/**
	 * Bind Events
	 */
	this.bind = function() {
		
		// Compile manifest
		$(document).on('click', '#manifests-compile-btn', function() {
			lense.api.request.submit('manifest_compile', {
				manifest: JSON.parse(self.editor.getValue())
			}, 'compileManifest');
		});
		
		// Execute manifest
		$(document).on('click', '#manifests-execute-btn', function() {
			lense.api.request.submit('manifest_execute', {
				manifest: JSON.parse(self.editor.getValue())
			}, 'executeManifest');
		});
	}
	
	/**
	 * Setup Manifest Editor
	 */
	this.setupEditor = function() {
		self.editor = ace.edit('manifests-editor');
		self.editor.setTheme('ace/theme/chrome');
		self.editor.getSession().setMode('ace/mode/json');
	}
});