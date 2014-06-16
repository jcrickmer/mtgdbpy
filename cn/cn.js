$(function() { 
    window.cn = {}; 
    cn.initToolTips = function() {  
        $(document).tooltip({  
            items: "img, [data-mid], [title]", 
            tooltipClass:'preview-tip', 
            content: function(callback) {  
                var element = $(this);
				console.dir(element);
                //if (element.is("[data-mid]")) { /* && (elements.is("[tip]") || element.is("[act-tip]"))) {  // for some reason, WordPress is eating these attributes */
                //    var text = element.text();  
                //    return "<img class='card' alt='" + text + "'" +  
                //        " src='http://gatherer.wizards.com/Handlers/Image.ashx?multiverseid="
                //        + element.attr("data-mid") + "&type=card" +  
                //        "'><div>" + text + "</div>";  
				var dataMidVal = element.text();
				var dataMid = element.attr("data-mid");
				var result = "waiting...";
// REVSIT - need to make this so it only happens once per page load. No need to keep going back to the server.
                $.ajax({
					url: "/cards/" + dataMid + "/",
					dataType: "json",
					async: false,
					complete: function(data) {
						console.log("I have completeness");
						var envelop = data.responseJSON;
						//console.dir(envelop);
						result = "<img src=\"" + envelop.img_url + "\" class=\"card\" alt=\""+ envelop.card.name + "\"><div>I have " + envelop.card.name + "</div>";
					},
				});
				//return function(f) { return "<div id='tt_" + dataMidVal + "'>waiting...</div>"; };
				return result;
            }
        });  
    };  
    cn.init = function() {  
        cn.initToolTips(); 
    }; 
}); 

$(function() {cn.init();});
