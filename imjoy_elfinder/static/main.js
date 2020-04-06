/**
 * elFinder client options and main script for RequireJS
 *
 * Rename "main.default.js" to "main.js" and edit it if you need configure elFInder options or any things. And use that in elfinder.html.
 * e.g. `<script data-main="./main.js" src="./require.js"></script>`
 **/
(function(){
	"use strict";
	var jqver = '3.4.1', uiver = '1.12.1';
		
	// Detect language (optional)
	var lang = (function() {
		var locq = window.location.search,
			map = {
				'pt' : 'pt_BR',
				'ug' : 'ug_CN',
				'zh' : 'zh_CN'
			},
			full = {
				'zh_tw' : 'zh_TW',
				'zh_cn' : 'zh_CN',
				'fr_ca' : 'fr_CA'
			},
			fullLang, locm, lang;
		if (locq && (locm = locq.match(/lang=([a-zA-Z_-]+)/))) {
			// detection by url query (?lang=xx)
			fullLang = locm[1];
		} else {
			// detection by browser language
			fullLang = (navigator.browserLanguage || navigator.language || navigator.userLanguage || '');
		}
		fullLang = fullLang.replace('-', '_').substr(0,5).toLowerCase();
		if (full[fullLang]) {
			lang = full[fullLang];
		} else {
			lang = (fullLang || 'en').substr(0,2);
			if (map[lang]) {
				lang = map[lang];
			}
		}
		return lang;
	})()
		
		// Start elFinder (REQUIRED)
	var start = function(elFinder, editors, config) {
		// load jQueryUI CSS
		elFinder.prototype.loadCss('//cdnjs.cloudflare.com/ajax/libs/jqueryui/'+uiver+'/themes/smoothness/jquery-ui.css');
		// config.defaultOpts.transport = new window.elFinderSupportVer1(null, connectorQuery]);
		if(config.extraQuery){
			config.defaultOpts.urlUpload = config.defaultOpts.url;
			if(config.defaultOpts.urlUpload.includes('?')){
				config.defaultOpts.urlUpload = config.defaultOpts.urlUpload + '&' + config.extraQuery
			}
			else{
				config.defaultOpts.urlUpload = config.defaultOpts.urlUpload + '?' + config.extraQuery
			}
		}
		else{
			config.defaultOpts.urlUpload = config.defaultOpts.url;
		}
		$(function() {
			var optEditors = {
					commandsOptions: {
						edit: {
							editors: Array.isArray(editors)? editors : []
						}
					}
				},
				opts = {};
			
			// Interpretation of "elFinderConfig"
			if (config && config.managers) {
				$.each(config.managers, function(id, mOpts) {
					opts = Object.assign(opts, config.defaultOpts || {});
					// editors marges to opts.commandOptions.edit
					try {
						mOpts.commandsOptions.edit.editors = mOpts.commandsOptions.edit.editors.concat(editors || []);
					} catch(e) {
						Object.assign(mOpts, optEditors);
					}
					// Make elFinder
					$('#' + id).elfinder(
						// 1st Arg - options
						$.extend(true, { lang: lang }, opts, mOpts || {}),
						// 2nd Arg - before boot up function
						function(fm, extraObj) {
							// `init` event callback function
							fm.bind('init', function() {
								// Optional for Japanese decoder "encoding-japanese"
								if (fm.lang === 'ja') {
									require(
										[ 'encoding-japanese' ],
										function(Encoding) {
											if (Encoding && Encoding.convert) {
												fm.registRawStringDecoder(function(s) {
													return Encoding.convert(s, {to:'UNICODE',type:'string'});
												});
											}
										}
									);
								}
							});
						}
					);
				});
			} else {
				alert('"elFinderConfig" object is wrong.');
			}
		});
	}

	// is IE8 or :? for determine the jQuery version to use (optional)
	var old = (typeof window.addEventListener === 'undefined' && typeof document.getElementsByClassName === 'undefined')
			||
			(!window.chrome && !document.unqueID && !window.opera && !window.sidebar && 'WebkitAppearance' in document.documentElement.style && document.body.style && typeof document.body.style.webkitFilter === 'undefined');

	// JavaScript loader (REQUIRED)
	function loadElFinder(elConfig) {
		elConfig = elConfig || {};
		elConfig['static_url'] = elConfig['static_url'] || '/static'
		elConfig['connector_url'] = elConfig['connector_url'] || '/connector/'
		elConfig['connector_query'] = elConfig['connector_query'] || null
		if(!elConfig['connector_url'].endsWith('/')) elConfig['connector_url'] = elConfig['connector_url'] + '/';

		// config of RequireJS (REQUIRED)
		require.config({
			baseUrl : 'js',
			paths : {
				'jquery'   : '//cdnjs.cloudflare.com/ajax/libs/jquery/'+(old? '1.12.4' : jqver)+'/jquery.min',
				'jquery-ui': '//cdnjs.cloudflare.com/ajax/libs/jqueryui/'+uiver+'/jquery-ui.min',
				'elfinder' : elConfig['static_url'] + '/js/elfinder.full',
				'elFinderSupportVer1' : elConfig['static_url'] + '/js/proxy/elFinderSupportVer1',
				'encoding-japanese': '//cdn.rawgit.com/polygonplanet/encoding.js/1.0.26/encoding.min'
			},
			waitSeconds : 10 // optional
		});

		define('elFinderConfig', {
			// elFinder options (REQUIRED)
			// Documentation for client options:
			// https://github.com/Studio-42/elFinder/wiki/Client-configuration-options
			defaultOpts : {
				url : elConfig['connector_url'], // connector URL (REQUIRED
				file_base_url: elConfig['file_base_url'],
				height: '100%',
				rememberLastDir: false,
				cssAutoLoad: true,
				themes : {
					'dark-slim'     : 'https://johnfort.github.io/elFinder.themes/dark-slim/manifest.json',
					'material'      : 'https://nao-pon.github.io/elfinder-theme-manifests/material-default.json',
					'material-gray' : 'https://nao-pon.github.io/elfinder-theme-manifests/material-gray.json',
					'material-light': 'https://nao-pon.github.io/elfinder-theme-manifests/material-light.json',
					'win10'         : 'https://nao-pon.github.io/elfinder-theme-manifests/win10.json'
				},
				// transport : new elFinderSupportVer1(),
				extraQuery: elConfig['connector_query'],
				onReady: elConfig['on_ready'],
				commandsOptions : {
					edit : {
						extraOptions : {
							// set API key to enable Creative Cloud image editor
							// see https://console.adobe.io/
							creativeCloudApiKey : '',
							// browsing manager URL for CKEditor, TinyMCE
							// uses self location with the empty value
							managerUrl : ''
						}
					}
					,quicklook : {
						// to enable CAD-Files and 3D-Models preview with sharecad.org
						sharecadMimes : ['image/vnd.dwg', 'image/vnd.dxf', 'model/vnd.dwf', 'application/vnd.hp-hpgl', 'application/plt', 'application/step', 'model/iges', 'application/vnd.ms-pki.stl', 'application/sat', 'image/cgm', 'application/x-msmetafile'],
						// to enable preview with Google Docs Viewer
						googleDocsMimes : ['application/pdf', 'image/tiff', 'application/vnd.ms-office', 'application/msword', 'application/vnd.ms-word', 'application/vnd.ms-excel', 'application/vnd.ms-powerpoint', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'application/vnd.openxmlformats-officedocument.presentationml.presentation', 'application/postscript', 'application/rtf'],
						// to enable preview with Microsoft Office Online Viewer
						// these MIME types override "googleDocsMimes"
						officeOnlineMimes : ['application/vnd.ms-office', 'application/msword', 'application/vnd.ms-word', 'application/vnd.ms-excel', 'application/vnd.ms-powerpoint', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'application/vnd.openxmlformats-officedocument.presentationml.presentation', 'application/vnd.oasis.opendocument.text', 'application/vnd.oasis.opendocument.spreadsheet', 'application/vnd.oasis.opendocument.presentation']
					}
				}
			},
			managers : {
				'elfinder': {},
			}
		});
		require(
			[
				'elfinder'
				, elConfig['static_url'] + '/js/extras/editors.default.js'               // load text, image editors
				, 'elFinderConfig'
			],
			start,
			function(error) {
				alert(error.message);
			}
		);
	}

	loadElFinder(window.ELFINDER_CONFIG);
})();