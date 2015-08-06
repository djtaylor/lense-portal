cs.import('CSUI3D', function() {
	
	// API response containers
	this.api_hosts  = [];
	this.api_groups = [];
	
	// Restructured groups object
	this.groups     = {};
	
	// Camera, scene, renderer
	this.camera, this.scene, this.renderer;
	
	// Controls
	this.controls;
	
	// Objects and targets
	this.objects = [];
	this.targets = {'all':[]};
	
	// Unique Index: THREE.Object3D
	THREE.Object3D.prototype.uindex = '';
	
	/**
	 * Initialize CSUI3D
	 * @constructor
	 */
	this.__init__ = function() {

		// Document ready
		$(document).ready(function() {
			self.set_canvas();
			self.init_canvas();
			self.click_host();
			self.position_hp();
		});
		
		// Window resize
		$(window).resize(function() {
			self.set_canvas();
			self.position_hp();
		});
		
		// Return the initialized class
		self.ui3d = self;
		return self;
	}
	
	/**
	 * Generate UUID
	 */
	this.uuid_gen = function() {
		var d = new Date().getTime();
	    var uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
	        var r = (d + Math.random()*16)%16 | 0;
	        d = Math.floor(d/16);
	        return (c=='x' ? r : (r&0x7|0x8)).toString(16);
	    });
	    return uuid;
	}
	
	/**
	 * Load Host Details
	 */
	this.load_host = function(h) {
		
		// First set up the loading gif
		$('#ui3d_host_inner_r').replaceWith(
			'<div id="ui3d_host_inner_r">' +
			'<div class="ui3d_host_loading">' +
			'<div class="ui3d_host_loading_txt">Loading host: ' + h + '</div>' +
			'<div class="ui3d_host_loading_gif"></div>' +
			'</div></div>'
		);
		
		// Position the element
		r_inner_mt  = ($('#ui3d_dw_inner').height() / 2) - ($('#ui3d_host_inner_r').height() / 2);
		r_inner_mlr = ($('#ui3d_dw_outer').width() - $('#ui3d_host_inner_r').width()) / 2;
		$('#ui3d_host_inner_r').css('margin-top', r_inner_mt + 'px');
		$('#ui3d_host_inner_r').css('margin-left', r_inner_mlr + 'px');
		$('#ui3d_host_inner_r').css('margin-right', r_inner_mlr + 'px');
		
		// Find the host details
		hd = null;
		$.each(self.api_hosts, function(i,o) {
			if (o.uuid == h) {
				hd = o;
				return false;
			}
		});
		
		// Update with the host details... IFRAMES NOOOOOO (just testing for now, I don't want to rewrite much)
		$('#ui3d_host_inner_r').replaceWith(
			'<div id="ui3d_host_inner_r">' +
			'<iframe class="ui3d_embed" src="http://192.168.218.130/hosts?panel=details&host=' + h + '"' +
			'</div>'
		);
		$('.ui3d_embed').height($('#ui3d_dw_outer').height());
	}
	
	/**
	 * Host Sorting
	 */
	this.sort_host = {
		'ip': function() {
			function inner(a,b) {
				aa = a.ip.split(".");
				bb = b.ip.split(".");
			    var resulta = aa[0]*0x1000000 + aa[1]*0x10000 + aa[2]*0x100 + aa[3]*1;
			    var resultb = bb[0]*0x1000000 + bb[1]*0x10000 + bb[2]*0x100 + bb[3]*1;
				return resulta-resultb;
			}
			self.api_hosts.sort(inner);
		},
		'name': function() {
			function inner(a,b) {
				if (a.name < b.name) { return -1; }
				if (a.name > b.name) { return 1;  }
				return 0;
			}
			self.api_hosts.sort(inner);
		},
		'os': function() {
			_sorted = {'linux':[],'windows':[]};
			$.each(self.api_hosts, function(i,h) {
				_sorted[h.os_type].push(h);
			});
			self.api_hosts = _sorted['linux'].concat(_sorted['windows']);
		},
		'groups': function() {
			_all    = [];
			_groups = {};
			$.each(self.api_hosts, function(i,h) {
				_all.push(h);
				ungrouped = true;
				$.each(self.api_groups, function(i,g) {
					if (!_groups.hasOwnProperty(g.name)) {
						_groups[g.name] = [];
					}
					$.each(g.members, function(i,m) {
						if ($.inArray(h.uuid, m) > -1) {
							_groups[g.name].push(h);
						}
					});
				});
			});
			self.groups = {
				'all':       _all,
				'directory': _groups
			}
		}
	}
	
	/**
	 * API Callback: Parse Hosts
	 */
	cs.callback['parse_hosts'] = function(c,m,d,a) {
		self.api_hosts = [];
		$.each(m, function(i,h) {
			h['uindex'] = self.uuid_gen();
			self.api_hosts.push(h);
		});
	}
	
	/**
	 * API Callback: Parse Groups
	 */
	cs.callback['parse_groups'] = function(c,m,d,a) {
		self.api_groups = m;
	}
	
	/**
	 * Load API Data
	 * 
	 * Asynchronous loading of API data when the document is ready. Wait to render the
	 * canvas until the hosts callback has been completed.
	 */
	this.load_api_data = function() {
		cs.api.submit('get', 'host', 'get', null, {'id': 'parse_hosts'});
		cs.api.submit('get', 'host/group', 'get', null, {'id': 'parse_groups'});
	}
	
	/**
	 * Click Host
	 */
	this.click_host = function() {
		
		// Bind to the host divs
		$(document).on('click', 'div[class$="host_outer"]', function(e) {
			a = cs.base.get_attr(e);
			$('#ui3d_dw').fadeToggle('fast', function() {
				self.load_host(a.host);
			});
		});
	}
	
	/**
	 * Position Host Popups
	 */
	this.position_hp = function() {
		ht = ($('#ui3d_canvas').height() / 2) - (200);
		$('.ui3d_host_popup').css('top', ht + 'px');
		$.each($('.ui3d_host_popup'), function(i,e) {
			a = cs.base.get_attr(e);
			$('div[class$="ui3d_host_popup"][host$="' + a.host + '"').draggable({
				handle: 'div[handle$="' + a.host + '"]',
				containment: 'parent'
			});
		});
	}
	
	/**
	 * Animate Canvas
	 */
	this.animate_canvas = function() {
		requestAnimationFrame(self.animate_canvas);
		TWEEN.update();
		self.controls.update();
	}
	
	/**
	 * Render Canvas
	 */
	this.render_canvas = function() {
		self.renderer.render(self.scene, self.camera);
	}
	
	/**
	 * Resize Canvas
	 */
	this.resize_canvas = function() {
		self.camera.aspect = window.innerWidth / window.innerHeight;
		self.camera.updateProjectionMatrix();
		self.renderer.setSize(window.innerWidth, window.innerHeight);
		self.render_canvas();
	}
	
	/**
	 * Transform Canvas
	 */
	this.transform_canvas = function(targets, duration) {
		TWEEN.removeAll();
		$.each(self.objects, function(i,o) {
			var object = self.objects[i];
			$.each(self.targets, function(tk, to) {
				var target = to[i];

				new TWEEN.Tween(object.position)
					.to({x:target.position.x, y:target.position.y, z:target.position.z}, Math.random() * duration + duration)
					.easing(TWEEN.Easing.Exponential.InOut)
					.start();

				new TWEEN.Tween(object.rotation)
					.to({x:target.rotation.x, y:target.rotation.y, z:target.rotation.z}, Math.random() * duration + duration)
					.easing(TWEEN.Easing.Exponential.InOut)
					.start();
			});
		});

		// Render the easing animation between states
		new TWEEN.Tween(this)
			.to({}, duration * 2)
			.onUpdate(self.render_canvas)
			.start();
	}
	
	/**
	 * Sort Canvas
	 */
	this.sort_canvas = function() {
		
		// Scan every host object
		$.each(self.api_hosts, function(i,h) {
			
			// Look through each target group
			$.each(self.targets, function(tk, tg) {
				rc_limit = 3;
				rc_count = 0;
				row_num  = 1;
				
				// Position each host in a target group
				$.each(tg, function(gk, gh) {
					rc_count++;
					if (rc_count > rc_limit) {
						rc_count = 1;
						row_num++;
					}
					if (gh.uindex == h.uindex) {
						gh.position.x = (rc_count * 200 ) - 1330;
						gh.position.y = - (row_num * 200 ) + 990;
					}
				});
			});
		});
	}
	
	/**
	 * Generate THREE.Object3D
	 * 
	 * Helper method used to generate a 3D object, used to define the final location
	 * of a host element on the canvas.
	 * 
	 * @param  {h}  The host details object
	 * @param  {rc} The column the host object should occupy in the host group
	 * @param  {rn} The row the host object should occupy in the host group
	 * @return THREE.Object3D
	 */
	this.obj_3d = function(h,rc,rn) {
		var o = new THREE.Object3D();
		o.position.x = rc * 200;
		o.position.y = rn * 200;
		o.uindex = h.uindex;
		return o;
	}
	
	/**
	 * Generate THREE.CSS3DObject
	 * 
	 * Helper method used to generate a CSS3D object. Object is initially rendered
	 * off the page, then animated into place on page load.
	 * 
	 * @param  {c} The child object to initialize the object with
	 * @return THREE.CSS3DObject
	 */
	this.obj_css3d = function(c) {
		var o = new THREE.CSS3DObject(c);
		o.position.x = Math.random() * 4000 - 2000;
		o.position.y = Math.random() * 4000 - 2000;
		o.position.z = Math.random() * 4000 - 2000;
		return o;
	}
	
	/**
	 * Generate Host Group Label
	 * 
	 * Helper method used to generate the host group label for any number of host
	 * objects.
	 * 
	 * @param  {i} The element group identifier
	 * @param  {l} The label for the host group to display
	 * @return An array containing the host group element and host container
	 */
	this.host_group_label = function(i,l) {
		
		// The label group
		var tc = $('<div></div>');
		tc.addClass('ui3d_group');
		tc.attr('table', 'all');
		
		// The table title
		var tt = $('<div></div>');
		tt.addClass('ui3d_group_label');
		tt.text('All Hosts');
		tc.append(tt);
		
		// Create a new CSS3D object
		css3d_obj = self.obj_css3d(tc[0]);
		
		// Create the CSS host group object
		var obj_3d = new THREE.Object3D();
		obj_3d.position.x = 240;
		obj_3d.position.y = 330;
		self.targets.all.push(obj_3d);
		
		// Generate and append the 3D object to the targets global
		self.objects.push(css3d_obj);
		
		// Add to the scene
		self.scene.add(css3d_obj);
	}
	
	/**
	 * Generate Host Object
	 * 
	 * Helper method used to generate a host object and append to the global
	 * targets and objects arrays.
	 * 
	 * @param  {h}  The host details objects from the API response
	 * @param  {p}  The parent object to attach to
	 * @param  {rc} The column the host object should occupy in the host group
	 * @param  {rn} The row the host object should occupy in the host group
	 * @return css_object
	 */
	this.host_object = function(h,rc,rn) {
		
		// Create the host container element
		var ho = $('<div></div>');
		ho.addClass('host_outer');
		ho.attr('host', h.uuid);
		
		// Create a new host element
		var he = $('<div></div>');
		he.addClass('host_inner');
		he.attr('host', h.uuid);
		ho.append(he);
		
		// Host icon
		var hi = $('<div></div>');
		hi.addClass('icon');
		hi.addClass('icon_' + h.os_type);
		he.append(hi);

		// Host name
		var hn = $('<div></div>');
		hn.addClass('name');
		hn.text(h.name);
		he.append(hn);

		// Host details
		var hd = $('<div></div>');
		hd.addClass('details');
		hd.text(h.ip);
		he.append(hd);

		// Create the CSS host object
		css3d_obj = self.obj_css3d(ho[0]);
		self.objects.push(css3d_obj);
		
		// Generate and append the 3D object to the targets global
		self.targets.all.push(self.obj_3d(h,rc,rn));
		
		// Add to the scene
		self.scene.add(css3d_obj);
	}
	
	/**
	 * Initialize Canvas
	 */
	this.init_canvas = function() {
		
		// Wait for the API response
		self.load_api_data();
		setTimeout(function() {
			
			// Set up the camera
			self.camera = new THREE.PerspectiveCamera(40, window.innerWidth / window.innerHeight, 1, 10000);
			self.camera.position.z = 3000;
			
			// Initialize the scene
			self.scene = new THREE.Scene();
			
			// Generate a host label object
			self.host_group_label('all', 'All Hosts');
			
			// Construct the initial table view and objects
			var rl = 10, rc = 0, rn = 1;
			$.each(self.api_hosts, function(i,h) {
				rc++;
				if (rc > rl) {
					rc = 1;
					rn++;
				}
				
				// Generate the host object and add to the scene
				self.host_object(h,rc,rn);
			});
			
			// Set up the renderer
			self.renderer = new THREE.CSS3DRenderer();
			self.renderer.setSize(window.innerWidth, window.innerHeight);
			self.renderer.domElement.style.position = 'absolute';
			document.getElementById('ui3d_canvas').appendChild(self.renderer.domElement);

			// Set up the controls
			self.controls = new THREE.TrackballControls(self.camera, self.renderer.domElement);
			self.controls.rotateSpeed = 0.5;
			self.controls.minDistance = 500;
			self.controls.maxDistance = 6000;
			self.controls.noRotate = true;
			self.controls.addEventListener('change', self.render_canvas);

			// Sorting options
			$.each($('div[sort]'), function(i,o) {
				a = cs.base.get_attr(o);
				$(document).on('click', 'div[sort$="' + a.sort + '"]', function(e) {
					_a = cs.base.get_attr(e);
					self.sort_host[_a.sort]();
					self.sort_canvas();
					self.transform_canvas(self.targets, 1000);
				});
			});
			
			// Default sorting view
			self.transform_canvas(self.targets, 1000);

			// On window resize
			$(window).resize(function() {
				self.resize_canvas();
			});
			
			// Loading animation
			self.animate_canvas();
		}, 1000);
	}
	
	/**
	 * Set WebGL Canvas Size
	 */
	this.set_canvas = function() {
		function _get_px_val(s) {
			var rx = /(^\d+)px$/g;
			var ra = rx.exec(s);
			return parseInt(ra[1]);
		}
		
		// Padding for base window
		bp = {
			'l': _get_px_val($('.base_window_min').css('padding-left')),
			'r': _get_px_val($('.base_window_min').css('padding-right')),
			't': _get_px_val($('.base_window_min').css('padding-top')),
			'b': _get_px_val($('.base_window_min').css('padding-bottom'))
		}
		
		// Define the width and height of the canvas element
		cn_width  = (window.innerWidth - (bp.l + bp.r));
		cn_height = (window.innerHeight - (bp.t + bp.b));
	
		// Set the width and height of the canvas element
		$('#ui3d_canvas').width(cn_width);
		$('#ui3d_canvas').height(cn_height);
		
		// Set the height of the host details pane
		$('#ui3d_dw').height(window.innerHeight);
		$('#ui3d_dw_outer').height(window.innerHeight - 60);
		$('#ui3d_dw_inner').height(window.innerHeight - 60);
		
		// Draggable container to fix jumping issues
		$('#ui3d_dw').draggable();
		
		// Resizable details window
		$('#ui3d_dw_outer').resizable({
			handles: {
				'w': '#ui3d_dw_resize'
			},
			alsoResize: '#ui3d_host_inner',
			resize: function() {
				$(this).css('left', 0);
				$('#ui3d_dw_inner').width($('#ui3d_dw_outer').width());
			}
		});
		
		// Set the height of any external content
		$('.ui3d_embed').width($('#ui3d_dw_outer').width());
		$('.ui3d_embed').height($('#ui3d_dw_outer').height());
	}
});