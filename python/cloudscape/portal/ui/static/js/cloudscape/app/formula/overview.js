cs.import('CSFormulaOverview', function() {

	/**
	 * Callback: Delete Formula
	 * 
	 * @param {d} The formula data object
	 */
	cs.register.callback('formula.delete', function(c,m,d,a) {
		$('div[class="table_row"][formula="' + d.uuid + '"]').remove();
	});

	/**
	 * Callback: Create Formula
	 * 
	 * @param {d} The formula data object
	 */
	cs.register.callback('formula.create', function(c,m,d,a) {
		d.internal = (d.internal === true) ? 'Yes': 'No';
		
		// Target row group
		t_rows = (d.type == 'group') ? 'group' : 'srv_util';
		
		// Create the new formula row
		$('div[type="rows"][target="formula"][f_type="' + t_rows + '"]').prepend(cs.layout.create.element('div', {
			css:  'table_row',
			attr: {
				formula: d.uuid
			},
			children: (function() {
				var c = [];
				
				// Formula select column
				c.push(cs.layout.create.element('div', {
					css: 'table_select_col',
					children: [cs.layout.create.element('input', {
						attr: {
							type:  'radio',
							name:  'formula_uuid',
							value: d.uuid
						}
					})]
				}));
				
				// Formula link column
				c.push(cs.layout.create.element('div', {
					css: 'table_col',
					attr: {
						col:    'formula_name',
						type:   'button',
						action: 'link',
						target: 'formula?panel=details&formula=' + d.uuid
					},
					text: d.name
				}));
				
				// Additional formula attributes
				var a = ['label', 'requires', 'edit_lock', 'type', 'internal'];
				$.each(a, function(i,v) {
					c.push(cs.layout.create.element('div', {
						css:  'table_col',
						attr: {
							col: 'formula_' + v,
						},
						text: (d.hasOwnProperty(v)) ? d[v] : null
					}));
				});
				return c;
			})()
		}));
		
		// Refresh the page layout
		cs.layout.refresh();
	});
});