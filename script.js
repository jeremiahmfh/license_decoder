#!/usr/bin/env node

/*
 * SA Drivers License Decoder
 * Modified to accept HEX input from command line
 * Usage:
 *    node script.js HEXSTRING
 */

var SALicenseParser = (function () {

  function parseFromBytes(bytes) {

    var thisLicense = {
      idNumber: '',
      idNumberType: '',
      idCountryOfIssue: '',
      surname: '',
      gender: '',
      initials: '',
      birthDate: '',
      driverRestrictions: '',
      licenseCountryOfIssue: 'ZA',
      licenseIssueNumber: '01',
      licenseNumber: '',
      licenseValidityStart: '',
      licenseValidityExpiry: '',
      professionalDrivingPermitExpiry: null,
      professionalDrivingPermitCodes: [],
      vehicleLicenses: {
          code: '',
          restriction: '',
          firstIssueDate: ''
      }
    };

    // ---- HEADER SECTION ----
    var headerSection = {
        barcodeVersionNumber: bytes[0],
        stringSectionLength: bytes[5],
        binarySectionLength: bytes[7]
    };

    var stringSectionStartPostion = 10;
    var stringSectionLength = bytes[5];
    var stringSectionEndPostion = stringSectionStartPostion + stringSectionLength;

    var stringSection = String.fromCharCode.apply(
        null,
        bytes.slice(stringSectionStartPostion, stringSectionEndPostion)
    );

    var arr = [];
    var sS = stringSection.length;

    for (var i = 0; i < sS; i++) {

      if (stringSection[i].charCodeAt(0) !== 225 &&
          stringSection[i].charCodeAt(0) !== 224) {

        if (i === 0) arr[i] = stringSection[i];
        else {
          if (arr[arr.length - 1] === '') {
            arr[arr.length - 1] = stringSection[i];
          }
          else arr[arr.length - 1] += stringSection[i];
        }
      }
      else {
        if (arr[arr.length - 1] !== '') {
          arr[arr.length] = '';
        }
      }
    }

    // ---- MAP FIELDS ----
    thisLicense.vehicleLicenses.code = arr[0] || '';
    thisLicense.surname = arr[1] || '';
    thisLicense.initials = arr[2] || '';
    thisLicense.idCountryOfIssue = arr[3] || '';
    thisLicense.licenseCountryOfIssue = arr[4] || '';
    thisLicense.vehicleLicenses.restriction = arr[5] || '';
    thisLicense.licenseNumber = arr[6] || '';
    thisLicense.idNumber = arr[7] || '';

    return thisLicense;
  }

  return {
    parseFromBytes: parseFromBytes
  };

})();


// ===============================
// Command Line Execution
// ===============================
if (require.main === module) {

  const hexInput = process.argv[2];

  if (!hexInput) {
    console.error("Usage: node script.js HEXSTRING");
    process.exit(1);
  }

  try {
    const buffer = Buffer.from(hexInput, "hex");
    const bytes = new Uint8Array(buffer);

    const result = SALicenseParser.parseFromBytes(bytes);

    console.log(JSON.stringify(result, null, 4));

  } catch (err) {
    console.error("Error decoding:", err.message);
    process.exit(1);
  }
}
