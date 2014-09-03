cs.import('CSFormulaRun', function() {

	// Actions Map
	this.actions = {}
	
	/**
	 * Initializ CSFormulaRun
	 * @constructor
	 */
	this.__init__ = function() {
		
		// Document ready
		$(document).ready(function() {
			cs.formula.run.parse_actions();
			cs.formula.run.bind_actions();
		});
	}
	
	/**
	 * Host NIC Dropdown
	 * 
	 * @param {c} Return code
	 * @param {m} Message body
	 * @param {d} Data object
	 */
	cs.register.callback('formula.host_nic_select', function(c,m,d,a) {
		host_uuid = m.uuid;
		host_nics = {}
		
		// Process each NIC
		params_block = '';
		$.each(m.sys.network, function(i,n) {
			
			// Set host NICs for the dropdown
			host_nics[n.id] = n.ipv4.addr;
		});
		
		// Set the name and render the dropdown
		name = (a.hasOwnProperty('append') && a.append !== false) ? a.name : a.parent + '_' + a.name;
		cs.formula.run.render_dropdown(a.parent, name, 'Host Network Adapter', host_nics);
	});
	
	/**
	 * Render Dropdown Menu
	 */
	this.render_dropdown = function(p,n,l,di) {
		
		// Construct the dropdown menu
		menu = cs.forms.create.dropdown({
			items: di,
			name:  n,
			label: l,
			form:  'run_formula',
			type:  'formula'
		});
		
		// If the dropdown has already been rendered, replace
		$('div[class$="formula_content_dynamic"][name$="' + p + '"]').css('display', 'block');
		if ($('div[class$="formula_field"][name$="' + n + '"]').length > 0) {
			$('div[class$="formula_field"][name$="' + n + '"]').replaceWith(menu);
		} else {
			$($('div[class$="formula_content_dynamic"][name$="' + p + '"]')).append(menu);
		}
		
		// Refresh the forms object
		cs.forms.load();
	}
	
	/**
	 * Parse Actions
	 */
	this.parse_actions = function() {
		$.each($('action'), function(ai,ao) {
			aa = get_attr(ao);
			if (!cs.formula.run.actions.hasOwnProperty(aa.t)) {
				cs.formula.run.actions[aa.t] = {}
			}
			
			// API Requests
			if (aa.t == 'api') {
				cs.formula.run.actions[aa.t][aa.i] = function(data, cbargs) {
					callback = null
					if ('c' in aa) {
						callback = { 'id': aa.c, 'args': cbargs }
					}
					
					// Submit the API request
					cs.api.request.submit(aa.m, {
						path: 	  aa.p,
						action:   aa.a,
						_data: 	  data,
						callback: callback
					});
				}
			}
		});
	}
	
	/**
	 * Bind Actions
	 */
	this.bind_actions = bind_actions;
	function bind_actions() {
		$.each($('bind'), function(bi,bo) {
			ba = get_attr(bo);
			$(ba.select).on(ba.event, function() {
				$.each($(bo).find('trigger'), function(ti,to) {
					ta = get_attr(to);
					tp = {}
					
					// Build out the parameters object
					$.each($(to).find('param'), function(pi,po) {
						pa = get_attr(po);
						ps = pa.filter.split('::');
						pk = pa.key;
						pv = null;
						if (ps[0] == 'query_val') {
							pv = $(ps[1]).val();
						}
						tp[pk] = pv;
					});
					
					// Build out any callback arguments
					cbargs = {}
					$.each($(to).find('cbarg'), function(ci,co) {
						ca = get_attr(co);
						cbargs[ca.key] = ca.value;
					});
					
					// Trigger the action
					cs.formula.run.actions[ta.type][ta.id](tp, cbargs);
				});
			});
		});
	}
});