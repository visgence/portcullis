/**
 * Yet another jquery color picker plugin,simple is the best.
 * @author levinhuang
 * @site http://www.vivasky.com
 * @note It's the jquery version of "Prototype color picker" by Myles Eftos,BUT a refined version.
 * Visit the raw prototype version here:myles.eftos.id.au/blog/2006/04/13/javascript-colour-picker-based-on-prototype/
 */
;(function($) {
    // Private functions.
    var p = {};
	p.getId=function(){
		var id=$(document).data("icolorID");
		if(!id){id=1;}else{id=id+1;};
		$(document).data("icolorID",id);
		return id;
	};
	p.colorMap=["00","33","66","99","AA","CC","EE","FF"];
    p.M = function($t,opts){ 
		this.$t=$t;
		this.$layout=null;/* set after _init */
		this.$colors=null;
		this.$tb=null;			/* color element table */
		this.flat=opts.flat;
		this.colors=opts.colors;
		this.trigger=opts.trigger;
		this.className=opts.cl;
		this.showInput=opts.showInput;
		this.defaultColor=!(this.colors&&this.colors.length>0);
		this.curColor="";
		this._opts=opts;
		
		this._init();
	};
	p.M.prototype={
		_init:function(){
			this._initColors();
			this._initCbk();
			this._initLayout();
		},
		_initColors:function(){
			if(!this.defaultColor) return;
			for(var i=0;i<p.colorMap.length;i++)
				this.colors.push(p.colorMap[i]+p.colorMap[i]+p.colorMap[i]);
			//blue
			for(var i=1;i<p.colorMap.length;i++){
				if(i!=4&&i!=6)
					this.colors.push(p.colorMap[0]+p.colorMap[0]+p.colorMap[i]);
			};
			for(var i=1;i<p.colorMap.length;i++){
				if(i!=2&&i!=4&&i!=6&&i!=7)
					this.colors.push(p.colorMap[i]+p.colorMap[i]+p.colorMap[7]);
			};
			//green
			for(var i=1;i<p.colorMap.length;i++){
				if(i!=4&&i!=6)
					this.colors.push(p.colorMap[0]+p.colorMap[i]+p.colorMap[0]);
			};
			for(var i=1;i<p.colorMap.length;i++){
				if(i!=2&&i!=4&&i!=6&&i!=7)
					this.colors.push(p.colorMap[i]+p.colorMap[7]+p.colorMap[i]);
			};
			//red
			for(var i=1;i<p.colorMap.length;i++){
				if(i!=4&&i!=6)
					this.colors.push(p.colorMap[i]+p.colorMap[0]+p.colorMap[0]);
			};
			for(var i=1;i<p.colorMap.length;i++){
				if(i!=2&&i!=4&&i!=6&&i!=7)
					this.colors.push(p.colorMap[7]+p.colorMap[i]+p.colorMap[i]);
			};
			//yellow
			for(var i=1;i<p.colorMap.length;i++){
				if(i!=4&&i!=6)
					this.colors.push(p.colorMap[i]+p.colorMap[i]+p.colorMap[0]);
			};
			for(var i=1;i<p.colorMap.length;i++){
				if(i!=2&&i!=4&&i!=6&&i!=7)
					this.colors.push(p.colorMap[7]+p.colorMap[7]+p.colorMap[i]);
			};
			//cyan
			for(var i=1;i<p.colorMap.length;i++){
				if(i!=4&&i!=6)
					this.colors.push(p.colorMap[0]+p.colorMap[i]+p.colorMap[i]);
			};
			for(var i=1;i<p.colorMap.length;i++){
				if(i!=2&&i!=4&&i!=6&&i!=7)
					this.colors.push(p.colorMap[i]+p.colorMap[7]+p.colorMap[7]);
			};										
			//megenta
			for(var i=1;i<p.colorMap.length;i++){
				if(i!=4&&i!=6)
					this.colors.push(p.colorMap[i]+p.colorMap[0]+p.colorMap[i]);
			};
			for(var i=1;i<p.colorMap.length;i++){
				if(i!=2&&i!=4&&i!=6&&i!=7)
					this.colors.push(p.colorMap[7]+p.colorMap[i]+p.colorMap[7]);
			};			
		},
		_initLayout:function(){
			var _this=this;
			//beforeInit callback
			var go=true;
			if(this._opts.beforeInit){go=this._opts.beforeInit();};
			if(!go) return;
			//build the layout
			this._opts.col=this._opts.col||this.colors.length;
			var colNum=this.defaultColor?8:(this._opts.col<1?1:this._opts.col);
			var html='<div class="'+this.className+'" id="icolor_'+p.getId()+'">',title="";
			html+='<table class="icolor_ct">';
			
			for(var i=0;i<this.colors.length;i++){
				if(i%colNum==0){
					html+="<tr>";
				};
				title=this._opts.title?(' title="#'+this.colors[i]+'"'):"";
				html+='<td style="background-color:#'+this.colors[i]+';"'+title+' abbr="'+this.colors[i]+'"></td>';
				if(i%colNum==(colNum-1)){
					html+="</tr>";
				};
			};
			
			html+='</table>';
			if(this.showInput){
				html+='<div class="icolor_ft"><input type="text" name="icolor" class="icolor_tbx"/>'+this._opts.okTpl+'</div>';
			};
			html+='</div>';
			//insert into the dom tree
			this.$layout=$(html);
			this.$tb=this.$layout.find("table");
			this.$colors=this.$tb.find("td");
			if(this.flat){
				this.$t.append(this.$layout.addClass("icolor_flat"));
			}else{
				$("body").append(this.$layout.hide());
			};
			//register event handlers
			this.$colors.click(function(e){
				if(this.className=="hot") return;
				_this.$colors.removeClass();
				$(this).addClass("hot");
				_this.curColor="#"+this.abbr;
				if(_this._$ipt) _this._$ipt.val(_this.curColor);
				_this.submit();
			});
			
			if(this._opts.hover){
				this.$colors.mouseenter(function(e){
					var c="#"+this.abbr;
					_this._opts.onOver?_this._opts.onOver(c):(function(){
						_this._$ipt.css("background-color",c);
					})();
				});
				this.$tb.mouseleave(function(e){
					_this._opts.onOut?_this._opts.onOut():(function(){
						_this._$ipt.css("background-color","");
					})();
				});
			};
			
			if(this.showInput){
				this._$ipt=this.$layout.find(".icolor_tbx").keyup(function(e){
					if(e.keyCode!=13) return;
					var v="";
					if((v=_this._$ipt.val())==""||v.indexOf("#")!=0) return;
					_this.curColor=v;
					_this.submit();
				});
				this.$layout.find(".icolor_ok").click(function(e){
					var v="";
					if((v=_this._$ipt.val())==""||v.indexOf("#")!=0) return false;
					_this.curColor=v;
					_this.submit();
					return false;
				});				
			};
			
			if(!this.flat){
				this.$t.bind(this.trigger,function(e){
					if(_this.$layout.is(":hidden"))
						_this.show();
					else
						_this.$layout.hide();
						
					return false;
				});
			};
			
			//afterInit callback
			if(this._opts.afterInit)	
				this._opts.afterInit();
		},
		show:function(){
			var _this=this;
			var pos=this.$t.offset(),cbk=this._opts.onShow?function(){_this._opts.onShow(pos);}:null;
			this.$layout.css({left:pos.left,top:pos.top+this.$t.height()});
			if(this._opts.slide){
				this.$layout.slideDown("fast",cbk);
			}else{
				this.$layout.show(0,cbk);
			};
		},
		submit:function(){
			if(this._opts.onSelect){this._opts.onSelect(this.curColor);};
			if((!this.flat)&&this._opts.autoClose){
				this.$layout.hide();
			};
		},
		/**
		 * Generate a proxy function  for the specified function 'f',
		 * which will set the 'this' keyword inside the f to the current p.M instance.
		 * @param {Function} f
		 */
		_proxy:function(f){
			if(!f) return null;
			var i=this;
			return function(){
				return f.apply(i,arguments);
			};
		},
		_initCbk:function(){
			//onShow
			this._opts.onShow=this._proxy(this._opts.onShow);
			//onSelect
			this._opts.onSelect=this._proxy(this._opts.onSelect);
			//beforeInit
			this._opts.beforeInit=this._proxy(this._opts.beforeInit);
			//afterInit
			this._opts.afterInit=this._proxy(this._opts.afterInit);
			//onOver
			this._opts.onOver=this._proxy(this._opts.onOver);
			//onOut
			this._opts.onOut=this._proxy(this._opts.onOut);
		}
	};
    //main plugin body
    $.fn.icolor = function(opts) {
        // Set the options.
        opts = $.extend({}, $.fn.icolor.defaults, opts);

        // Go through the matched elements and return the jQuery object.
        return this.each(function() {
			var $i=$(this);
			if(!$i.data("icolor"))
				$i.data("icolor",new p.M($i,opts));
        });
    };
    // Public defaults.
    $.fn.icolor.defaults = {
        trigger: 'click',								/* event name for triggering to show icolor */
		flat:false,										/* inline mode */
		col:8,											/* column number of icolor */
		colors:[],										/* user predefined colors */
		showInput:false,								/* show a input box after the color elements */
		cl:"icolor",									/* css class for icolor */
		title:true,										/* whether include title attribute for the color element */
		autoClose:true,									/* auto-close after selecting a color  */		
		slide:true,										/* use the 'slideDown' effect when showing icolor */
		okTpl:'',										/* ok button template such as <button class="icolor_ok">х╥хо<button> */
		onShow:null,									/* onShow callback */
		onSelect:null,									/* onSelect callback */	
		beforeInit:null,								/* beforeInit callback */
		afterInit:null,									/* afterInit callback */
		onOver:null,									/* callback for mouseover a color element */	
		onOut:null,										/* callback for mouseout the whole icolor */
		hover:true										/* whether register hover event handlers to icolor */
    };
	//public methods
	$.fn.icolor.isDark=function(c){
	  	var colr = parseInt(c.substr(1), 16);
	  	return (colr >>> 16) // R
	    	+ ((colr >>> 8) & 0x00ff) // G 
	    	+ (colr & 0x0000ff) // B
	    	< 500;		
	};
})(jQuery);  