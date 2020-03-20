/**
 * elFinder transport to support old protocol.
 *
 * @example
 * $('selector').elfinder({
 *   .... 
 *   transport : new elFinderSupportVer1()
 * })
 *
 * @author Dmitry (dio) Levashov
 **/
window.elFinderSupportVer1 = function(upload, extra_query) {
	"use strict";
	var self = this,
		dateObj, today, yesterday,
		getDateString = function(date) {
			return date.replace('Today', today).replace('Yesterday', yesterday);
		};

	if(extra_query){
		this.extra_query = extra_query.startsWith('&')?extra_query.slice(1):extra_query;
	}
	else{
		this.extra_query = null;
	}
	
	dateObj = new Date();
	today = dateObj.getFullYear() + '/' + (dateObj.getMonth() + 1) + '/' + dateObj.getDate();
	dateObj = new Date(Date.now() - 86400000);
	yesterday = dateObj.getFullYear() + '/' + (dateObj.getMonth() + 1) + '/' + dateObj.getDate();
	
	this.upload = upload || 'auto';
	
	this.init = function(fm) {
		this.fm = fm;
		this.fm.parseUploadData = function(text) {
			var data;

			if (!$.trim(text)) {
				return {error : ['errResponse', 'errDataEmpty']};
			}

			try {
				data = JSON.parse(text);
			} catch (e) {
				return {error : ['errResponse', 'errDataNotJSON']};
			}
			
			return data;
		};
	};
	
	
	this.send = function(opts) {
		var self = this,
			fm = this.fm,
			dfrd = $.Deferred(),
			cmd = opts.data.cmd,
			args = [],
			_opts = {},
			data,
			xhr;
			
		dfrd.abort = function() {
			if (xhr.state() == 'pending') {
				xhr.quiet = true;
				xhr.abort();
			}
		};
		
		switch (cmd) {
			case 'open':
				opts.data.tree = 1;
				if(opts.data.target){
					var _file = fm.file(opts.data.target)
					opts.data.current = _file && _file.phash;
				}
				break;
			case 'parents':
			case 'tree':
				return dfrd.resolve({tree : []});
			case 'get':
				opts.data.cmd = 'read';
				opts.data.current = fm.file(opts.data.target).phash;
				break;
			case 'put':
				opts.data.cmd = 'edit';
				opts.data.current = fm.file(opts.data.target).phash;
				break;
			case 'dim':
				opts.data.cmd = 'dim';
				opts.data.current = fm.file(opts.data.target).phash;
				break;
			case 'archive':
			case 'rm':
				opts.data.current = fm.file(opts.data.targets[0]).phash;
				break;
			case 'extract':
			case 'rename':
			case 'resize':
				opts.data.current = fm.file(opts.data.target).phash;
				break;
			case 'duplicate':
				opts.data.current = fm.cwd().hash;
				break
			case 'mkdir':
				break
			case 'mkfile':
				break;
			case 'paste':
				opts.data.current = opts.data.dst;
				if (! opts.data.tree) {
					$.each(opts.data.targets, function(i, h) {
						if (fm.file(h) && fm.file(h).mime === 'directory') {
							opts.data.tree = '1';
							return false;
						}
					});
				}
				break;
				
			case 'size':
				return dfrd.resolve({error : fm.res('error', 'cmdsupport')});
			case 'search':
				break;
			case 'file':
				opts.data.cmd = 'open';
				opts.data.current = fm.file(opts.data.target).phash;
				break;
		}
		// cmd = opts.data.cmd
		
		if(this.extra_query){
			if(opts.url.includes('?')){
				opts.url = opts.url + '&' + this.extra_query
			}
			else{
				opts.url = opts.url + '?' + this.extra_query
			}
		}
		xhr = $.ajax(opts)
			.fail(function(error) {
				dfrd.reject(error);
			})
			.done(function(raw) {
				var migrated_cmds = ['rm', 'paste', 'rename', 'search', 'duplicate', 'mkdir', 'mkfile'];
				if(migrated_cmds.includes(cmd)){
					dfrd.resolve(raw);
					return;
				}
				else{
					data = self.normalize(cmd, raw);
					dfrd.resolve(data);
				}
				
			});
			
		return dfrd;
	};
	
	// fix old connectors errors messages as possible
	// this.errors = {
	// 	'Unknown command'                                  : 'Unknown command.',
	// 	'Invalid backend configuration'                    : 'Invalid backend configuration.',
	// 	'Access denied'                                    : 'Access denied.',
	// 	'PHP JSON module not installed'                    : 'PHP JSON module not installed.',
	// 	'File not found'                                   : 'File not found.',
	// 	'Invalid name'                                     : 'Invalid file name.',
	// 	'File or folder with the same name already exists' : 'File named "$1" already exists in this location.',
	// 	'Not allowed file type'                            : 'Not allowed file type.',
	// 	'File exceeds the maximum allowed filesize'        : 'File exceeds maximum allowed size.',
	// 	'Unable to copy into itself'                       : 'Unable to copy "$1" into itself.',
	// 	'Unable to create archive'                         : 'Unable to create archive.',
	// 	'Unable to extract files from archive'             : 'Unable to extract files from "$1".'
	// }
	
	this.normalize = function(cmd, data) {
		var self = this,
			fm   = this.fm,
			files = {}, 
			filter = function(file) { return file && file.hash && file.name && file.mime ? file : null; },
			getDirs = function(items) {
				return $.grep(items, function(i) {
					return i && i.mime && i.mime === 'directory'? true : false;
				});
			},
			getTreeDiff = function(files) {
				var dirs = getDirs(files);
				treeDiff = fm.diff(dirs, null, ['date', 'ts']);
				if (treeDiff.added.length) {
					treeDiff.added = getDirs(treeDiff.added);
				}
				if (treeDiff.changed.length) {
					treeDiff.changed = getDirs(treeDiff.changed);
				}
				if (treeDiff.removed.length) {
					var removed = [];
					$.each(treeDiff.removed, function(i, h) {
						var item;
						if ((item = fm.file(h)) && item.mime === 'directory') {
							removed.push(h);
						}
					});
					treeDiff.removed = removed;
				}
				return treeDiff;
			},
			phash, diff, isCwd, treeDiff;

		if ((cmd == 'tmb' || cmd == 'get' || cmd == 'dim')) {
			return data;
		}
		
		// if (data.error) {
		// 	$.each(data.error, function(i, msg) {
		// 		if (self.errors[msg]) {
		// 			data.error[i] = self.errors[msg];
		// 		}
		// 	});
		// }
		
		if (cmd == 'upload' && data.error && data.cwd) {
			data.warning = Object.assign({}, data.error);
			data.error = false;
		}
		
		
		if (data.error) {
			return data;
		}
		
		if (cmd == 'put') {

			phash = fm.file(data.target.hash).phash;
			return {changed : [data.target]};
		}
		
		phash = data.cwd && data.cwd.hash;

		isCwd = (phash == fm.cwd().hash);
		
		if (data.tree) {
			$.each(this.normalizeTree(data.tree), function(i, file) {
				files[file.hash] = file;
			});
		}
		
		$.each(data.cdc||[], function(i, file) {
			var hash = file.hash,
				mcts;

			if (files[hash]) {
				if (file.date) {
					mcts = Date.parse(getDateString(file.date));
					if (mcts && !isNaN(mcts)) {
						files[hash].ts = Math.floor(mcts / 1000);
					} else {
						files[hash].date = file.date || fm.formatDate(file);
					}
				}
				files[hash].locked = file.hash == phash ? true : file.rm === void(0) ? false : !file.rm;
			} else {
				files[hash] = file;
			}
		});
		
		if (!data.tree) {
			$.each(fm.files(), function(hash, file) {
				if (!files[hash] && file.phash != phash && file.mime == 'directory') {
					files[hash] = file;
				}
			});
		}
		
		if (cmd == 'open') {
			return {
					cwd     : files[phash] || data.cwd,
					files   : $.map(files, function(f) { return f; }),
					options : data.options,
					init    : !!data.params,
					debug   : data.debug
				};
		}
		
		if (isCwd) {
			diff = fm.diff($.map(files, filter));
		} else {
			if (data.tree && cmd !== 'paste') {
				diff = getTreeDiff(files);
			} else {
				diff = {
					added   : [],
					removed : [],
					changed : []
				};
				if (cmd === 'paste') {
					diff.sync = true;
				}
			}
		}
		
		return Object.assign({
			current : data.cwd && data.cwd.hash,
			error   : data.error,
			warning : data.warning,
			options : {tmb : !!data.tmb}
		}, diff);
		
	};
	
	/**
	 * Convert old api tree into plain array of dirs
	 *
	 * @param  Object  root dir
	 * @return Array
	 */
	this.normalizeTree = function(root) {
		var self     = this,
			result   = [],
			traverse = function(dirs, phash) {
				var i, dir;
				
				for (i = 0; i < dirs.length; i++) {
					dir = dirs[i];
					result.push(dir);
					dir.dirs.length && traverse(dir.dirs, dir.hash);
				}
			};

		traverse([root]);

		return result;
	};
	
	/**
	 * Convert file info from old api format into new one
	 *
	 * @param  Object  file
	 * @param  String  parent dir hash
	 * @return Object
	 */

};
