document.querySelectorAll('.usage-table .expn .expn-title[aria-expanded="false"]').forEach(element => {
    element.setAttribute('aria-expanded', 'true');
    element.click();
});

document.querySelectorAll('div.expn div.expn-title[aria-expanded="false"]').forEach(element => {
    element.setAttribute('aria-expanded', 'true');
    element.click();
});

function delay(time) {
  return new Promise(resolve => setTimeout(resolve, time));
}

delay(1000).then(() => {
    console.log('Scrap Data Complete');
    
    var usageTableContent = document.querySelector('.usage-table').innerHTML;
    convertToJSON(usageTableContent);
});

function convertToJSON(usageTableContent) {
    const parser = new DOMParser();
    const doc = parser.parseFromString(usageTableContent, 'text/html');

    const usageDatesElements = doc.querySelectorAll('.usage-dates');
    const numRequestsElements = doc.querySelectorAll('.num-requests');
    const tabularNumsElements = doc.querySelectorAll('.body-small.bold.tabular-nums');

    const data = Array.from(usageDatesElements).map((elem, index) => {
        const usageDateElem = elem.querySelector('.usage-date-local');
        const usageDate = usageDateElem ? usageDateElem.innerText.replace('Local time: ', '').trim() : null;

        const numRequest = numRequestsElements[index].innerText.split(',')[0];

        const tabularNumsText = tabularNumsElements[index].innerText;
        const tabularNumsMatches = tabularNumsText.match(/([\d,]+)\s*prompt.*?([\d,]+)\s*completion.*?([\d,]+)\s*token/);

        return {
            ID: "ID" + (index + 1),
            Date: usageDate,
            Model: numRequest,
            Prompt: tabularNumsMatches ? tabularNumsMatches[1].replace(/,/g, '') : null,
            Completion: tabularNumsMatches ? tabularNumsMatches[2].replace(/,/g, '') : null,
            Total: tabularNumsMatches ? tabularNumsMatches[3].replace(/,/g, '') : null,
        };
    });

    const csvHeaders = ["ID", "Date", "Model", "Prompt", "Completion", "Total"];
    const csvData = data.map(row => [
        row.ID,
        row.Date,
        row.Model,
        row.Prompt,
        row.Completion,
        row.Total,
    ].map(value => `"${value ? value.replace(/"/g, '""') : ''}"`).join(','));
    csvData.unshift(csvHeaders.join(','));
    const csvContent = csvData.join('\r\n');
    const csvBlob = new Blob([csvContent], { type: 'text/csv' });
    const csvLink = document.createElement('a');
    csvLink.href = URL.createObjectURL(csvBlob);
    csvLink.download = 'data_openai_usage_19_october_2023';
    csvLink.click();
}
//Add More Feature TBA