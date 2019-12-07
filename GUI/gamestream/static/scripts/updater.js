var myVar;
var robot1Health;
var timerStatus = false;
var startTime;

function showTime(){
    var d = new Date();
    var t = d.toLocaleTimeString();

    $.ajax({
      url: '/scoreboard/ajax/update/',
      type: 'GET',
      dataType: 'json',
      success: function (data) {
        if (data) {
          document.getElementById("redMetaTeamName").innerHTML = data.redMetaTeamName;
          document.getElementById("redRobot1Name").innerHTML = data.redRobot1Name;
          document.getElementById("redRobot2Name").innerHTML = data.redRobot2Name;
          document.getElementById("redRobot3Name").innerHTML = data.redRobot3Name;
          document.getElementById("redRobot4Name").innerHTML = data.redRobot4Name;
          $("#redNexus")
          .attr("aria-valuenow", data.redNexusHealth)
          .css("width", data.redNexusHealth + "%")
          .text(data.redNexusHealth);
          $("#redRobot1")
          .attr("aria-valuenow", data.redRobot1Health)
          .css("width", data.redRobot1Health + "%")
          .text(data.redRobot1Health);
          $("#redRobot2")
          .attr("aria-valuenow", data.redRobot2Health)
          .css("width", data.redRobot2Health + "%")
          .text(data.redRobot2Health);
          $("#redRobot3")
          .attr("aria-valuenow", data.redRobot3Health)
          .css("width", data.redRobot3Health + "%")
          .text(data.redRobot3Health);
          $("#redRobot4")
          .attr("aria-valuenow", data.redRobot4Health)
          .css("width", data.redRobot4Health + "%")
          .text(data.redRobot4Health);

          document.getElementById("blueMetaTeamName").innerHTML = data.blueMetaTeamName;
          document.getElementById("blueRobot1Name").innerHTML = data.blueRobot1Name;
          document.getElementById("blueRobot2Name").innerHTML = data.blueRobot2Name;
          document.getElementById("blueRobot3Name").innerHTML = data.blueRobot3Name;
          document.getElementById("blueRobot4Name").innerHTML = data.blueRobot4Name;
          $("#blueNexus")
          .attr("aria-valuenow", data.blueNexusHealth)
          .css("width", data.blueNexusHealth + "%")
          .text(data.blueNexusHealth);
          $("#blueRobot1")
          .attr("aria-valuenow", data.blueRobot1Health)
          .css("width", data.blueRobot1Health + "%")
          .text(data.blueRobot1Health);
          $("#blueRobot2")
          .attr("aria-valuenow", data.blueRobot2Health)
          .css("width", data.blueRobot2Health + "%")
          .text(data.blueRobot2Health);
          $("#blueRobot3")
          .attr("aria-valuenow", data.blueRobot3Health)
          .css("width", data.blueRobot3Health + "%")
          .text(data.blueRobot3Health);
          $("#blueRobot4")
          .attr("aria-valuenow", data.blueRobot4Health)
          .css("width", data.blueRobot4Health + "%")
          .text(data.blueRobot4Health);

          document.getElementById("arenaStage").innerHTML = data.arenaStage;
          document.getElementById("towerStatus").innerHTML = data.towerStatus;
          document.getElementById("arenaStatus").innerHTML = data.arenaStatus;
          if(data.arenaStatus == "On" && timerStatus == false) {
            startTime = d;
            timerStatus = true;
          }
          else if(data.arenaStatus == "On") {
            timerStatus = true;
          }
          else {
            timerStatus = false;
          }
        }
      }
    });

    if(timerStatus) {
      var currTime = d.getTime() - startTime.getTime();
      var minutes = parseInt(currTime/1000/60);
      var seconds = parseInt(currTime/1000)-minutes*60;
      document.getElementById("minutes").innerHTML = minutes.toString().padStart(2,"0");
      document.getElementById("seconds").innerHTML = seconds.toString().padStart(2,"0");
    }
    else {
      var minutes = 0;
      var seconds = 0;
      document.getElementById("minutes").innerHTML = minutes.toString().padStart(2,"0");
      document.getElementById("seconds").innerHTML = seconds.toString().padStart(2,"0");
    }
}
function stopFunction(){
    clearInterval(myVar); // stop the timer
}
$(document).ready(function(){
    startTime = 0;
    myVar = setInterval("showTime()", 1);
});
