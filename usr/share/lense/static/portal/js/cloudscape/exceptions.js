/**
 * ModuleNotFound
 * 
 * Tried to load a module that was not imported using 'cs.import'.
 * 
 * @param {m} The name of the module
 */
function ModuleNotFound(m) {
	this.name    = 'ModuleNotFound';
	this.message = 'Module <' + m + '> not found, must import using <cs.import>';
}
ModuleNotFound.prototype = Error.prototype;

/**
 * MethodNotFound
 * 
 * Tried to run a method that was not registered in the 'cs.method' object.
 * 
 * @param {m} The name of the method
 */
function MethodNotFound(m) {
	this.name    = 'MethodNotFound';
	this.message = 'Method <' + m + '> not found, must register using <cs.register.method>';
}
MethodNotFound.prototype = Error.prototype;

/**
 * CallbackNotFound
 * 
 * Tried to run an API callback that was not registered in the 'cs.callback' object.
 * 
 * @param {c} The name of the callback
 */
function CallbackNotFound(c) {
	this.name    = 'CallbackNotFound';
	this.message = 'Callback <' + c + '> not found, must register using <cs.register.callback>';
}
CallbackNotFound.prototype = Error.prototype;