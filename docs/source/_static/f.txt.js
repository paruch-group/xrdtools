$(document).ready(function() {
    $("dl.toggle > dd").hide();
    $("dl.toggle > dt").click(
        function(event){
            $(this).next().toggle(250);
        });
    });
