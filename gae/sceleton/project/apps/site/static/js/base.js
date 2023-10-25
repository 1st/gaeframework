$(document).ready(function(){

  /* Confirm operation (for all tags with class='confirm') */
  $(".confirm").live("click", function(){
    message = $(this).attr('title');
      if (! message) {
        message = $(this).text();
      }
      if (! message) {
        message = "Continue";
      }
      if (! confirm(message + "?")) {
        return false;
      }
  });

});