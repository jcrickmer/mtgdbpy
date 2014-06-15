$(function() { 
    window.cn = {}; 
    cn.initToolTips = function() {  
        $(document).tooltip({  
            items: "img, [data-mid], [title]",  
            content: function() {  
                var element = $( this );  
                if (element.is("[data-mid]")) { /* && (elements.is("[tip]") || element.is("[act-tip]"))) {  // for some reason, WordPress is eating these attributes */
                    var text = element.text();  
                    return "<img class='card' alt='" + text + "'" +  
                        " src='http://gatherer.wizards.com/Handlers/Image.ashx?multiverseid="
                        + element.attr("data-mid") + "&type=card" +  
                        "'><div>" + text + "</div>";  
                } 
            }  
         });  
    };  
    cn.init = function() {  
        cn.initToolTips(); 
    }; 
}); 

$(function() {cn.init();});
