////// EXAMPLE VALUE: DATES_WITH_TIMES
// const DATES_WITH_TIMES = [
//     {
//         date: "21-11-2024",
//         startTime: "09:30",
//         endTime: "18:00",
//         timePerSlot: 5,
//         location: "Online via MS Teams",
//         dateId: null
//     },
//     {
//         date: "22-11-2024",
//         startTime: "09:30",
//         endTime: "18:00",
//         timePerSlot: 5,
//         location: "Online via MS Teams",
//         dateId: null
//     }
// ];

const DATES_WITH_TIMES = [
    {
        date: "21-11-2024",
        startTime: "09:30",
        endTime: "10:00",
        timePerSlot: 5,
        location: "Online via MS Teams",
        dateId: null
    },
    {
        date: "22-11-2024",
        startTime: "09:30",
        endTime: "10:00",
        timePerSlot: 5,
        location: "Online via MS Teams",
        dateId: null
    }
];
const TIMEOUT = 1000;

let currentDate = 0;
let currentSlotDateIndex = 0;
let currentSlot = 0;

/**
 * Converts a time string to minutes since midnight.
 * @param {string} timeStr 
 * @returns {number}
 */
function timeStringToMinutes(timeStr) {
    const [hours, minutes] = timeStr.split(':').map(Number);
    return hours * 60 + minutes;
}

/**
 * Converts minutes since midnight back to a time string (HH:mm).
 * @param {number} minutes 
 * @returns {string}
 */
function minutesToTimeString(minutes) {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return `${hours.toString().padStart(2, '0')}:${mins.toString().padStart(2, '0')}`;
}

/**
 * Creates all dates from the DATES_WITH_TIMES array.
 */
function createDate() {
    if (currentDate >= DATES_WITH_TIMES.length) {
        console.log("All dates created. Updating IDs...");
        setTimeout(updateDateIds, TIMEOUT); // Wait for the UI to update before fetching IDs
        return;
    }

    const newDateBtn = document.querySelector('a#new-event-date-button');
    newDateBtn.click();

    // Wait for the modal to open
    setTimeout(() => {
        const inputDate = document.querySelector('input#EventDate_Date');
        inputDate.value = DATES_WITH_TIMES[currentDate].date;

        const inputLocation = document.querySelector('input#EventDate_Location');
        inputLocation.value = DATES_WITH_TIMES[currentDate].location;

        const saveButton = document.querySelector('button#save-event-date-button');
        saveButton.click();

        currentDate++;
        setTimeout(createDate, TIMEOUT); // Wait for the modal to close and start the next date
    }, TIMEOUT);
}

/**
 * Updates the IDs for each created date in the DATES_WITH_TIMES array.
 */
function updateDateIds() {
    const dateList = document.querySelector('div#event-date-list');
    const dateCards = dateList.querySelectorAll('div.card');

    dateCards.forEach((dateCard) => {
        const dateSpan = dateCard.querySelector('span.text-event-date');
        const date = dateSpan.textContent.trim();

        const btn = dateCard.querySelector('a[data-action="new-item"][data-item-type-id="3"]');
        const dateId = btn.getAttribute('data-date-id');

        const dateObj = DATES_WITH_TIMES.find(dateObj => dateObj.date === date);
        if (dateObj) {
            dateObj.dateId = dateId;
        }
    });

    console.log("Date IDs updated:", DATES_WITH_TIMES);
    setTimeout(createSlots, TIMEOUT); // Proceed to create slots after updating IDs
}

/**
 * Creates slots for the current date in the DATES_WITH_TIMES array.
 */
function createSlots() {
    if (currentSlotDateIndex >= DATES_WITH_TIMES.length) {
        console.log("All slots created.");
        return;
    }

    const { dateId, startTime, endTime, timePerSlot } = DATES_WITH_TIMES[currentSlotDateIndex];
    const startMinutes = timeStringToMinutes(startTime);
    const endMinutes = timeStringToMinutes(endTime);
    const numberOfSlots = Math.floor((endMinutes - startMinutes) / timePerSlot);

    if (currentSlot >= numberOfSlots) {
        currentSlot = 0;
        currentSlotDateIndex++;
        setTimeout(createSlots, TIMEOUT); // Move to the next date
        return;
    }

    const slotStartTime = minutesToTimeString(startMinutes + currentSlot * timePerSlot);
    const slotEndTime = minutesToTimeString(startMinutes + (currentSlot + 1) * timePerSlot);

    const newSlotBtn = document.querySelector(`a[data-date-id="${dateId}"][data-action="new-item"][data-item-type-id="3"]`);
    newSlotBtn.click();

    // Wait for the modal to open
    setTimeout(() => {
        const inputTitle = document.querySelector('input#Item_Title');
        inputTitle.value = 'Trajectcoaching';

        const inputStartTime = document.querySelector('input#Item_StartTime');
        inputStartTime.value = slotStartTime;

        const inputEndTime = document.querySelector('input#Item_EndTime');
        inputEndTime.value = slotEndTime;

        const inputMaxAmount = document.querySelector('input#Item_MaximumNumberOfParticipants');
        inputMaxAmount.value = '1';

        const saveButton = document.querySelector('button#save-event-date-item-button');
        saveButton.click();

        currentSlot++;
        setTimeout(createSlots, TIMEOUT); // Wait for the modal to close and start the next slot
    }, TIMEOUT);
}

// Start the process
createDate();
