/*

  NOTICE TO ANYONE BUILDING THEIR OWN FORK OF THIS PROJECT:

  This file is noted as a .js file however unless you have the ability to integrate it yourself without the need of the googlescript
  ide, then please refrain from taking using this on a website or webpage

*/


function checkCardNumber(CardNumber) {
  // Get the spreadsheet and sheet.
  var tLogSheet = SpreadsheetApp.openById("1zy07fuvIi8Zjh64PXCPjqMoRseUnffRyuTZYEWfh00Y").getSheetByName('MachinesToday');
  // Get the card number to check.
  var cardNumber = CardNumber;
  

  // Get the range of card numbers.
  var rangeOfUsers = tLogSheet.getRange('A:A');
  var rangeOfTimeouts = tLogSheet.getRange('D:D');

  // Get the values of the range.
  var values = rangeOfUsers.getValues();
  var secVals = rangeOfTimeouts.getValues();

  // Check if the card number is found in the values.
  var userInList = false;
  var seshFinished = false;
  var indexOfFound;
  for (var i = values.length - 1; i > 0; --i) {
    if (values[i] == cardNumber) {
      userInList = true;
      if(!secVals[i].isBlank()) {
        seshFinished = true;
      }
      indexOfFound = i;
      break;
    }
    
  }

  // If the time out is found create a new row.
  if (!userInList && !seshFinished) {
    var lastRow = sheet.getLastRow();
    var timestamp = new Date();
    var newCardRecord = sheet.getRange(lastRow+1,1).setValue(cardNumber);
    var newCardTimestamp = sheet.getRange(lastRow+1,9).setValue(timestamp);
  } else if(userInList && !seshFinished) {
    // If the card number is found, add a timestamp to the next column.
    var timestamp = new Date();
    Logger.log(indexOfFound);
    sheet.getRange(indexOfFound + 1, 10).setValue(timestamp);
  } else {
    var lastRow = sheet.getLastRow();
    var timestamp = new Date();
    var newCardRecord = sheet.getRange(lastRow+1,1).setValue(cardNumber);
    var newCardTimestamp = sheet.getRange(lastRow+1,9).setValue(timestamp);
  }
}

