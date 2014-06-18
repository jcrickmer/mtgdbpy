$(function() { 
    window.cn = {};
    cn.cardCache = {};
    cn.initToolTips = function() {  
        $(document).tooltip({  
            items: "[data-mid]", 
            tooltipClass:'preview-tip', 
            content: function(callback) {  
                var element = $(this);
				var dataMid = element.attr("data-mid");
				var result = "waiting...";
				var card = window.cn.cardCache['mid' + dataMid];
				if (card == null) {
					$.ajax({
						url: "/cards/" + dataMid + "/",
						dataType: "json",
						async: false,
						complete: function(data) {
							var envelop = data.responseJSON;
							if (envelop.status == 'success') {
								window.cn.cardCache['mid' + dataMid] = envelop.card;
							}
							card = envelop.card;
						},
					});
				}
				result = "<img src=\"" + card.img_url + "\" class=\"card\" alt=\""+ card.name + "\"><div>";
				return result;
            }
        });  
    };  
    cn.init = function() {  
        cn.initToolTips(); 
    }; 
}); 

$(function() {cn.init();});
