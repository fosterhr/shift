function convertTimestampToLocalTime(timestamp) {
    const date = new Date(timestamp * 1000); // Convert seconds to milliseconds

    const options = {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        timeZoneName: 'short'
    };
    const formattedDateTime = date.toLocaleString('en-US', options);
    const [datePart, timePart] = formattedDateTime.split(', ');

    return `${datePart} at ${timePart}`;
}