---
category: Other
date: 2023-01-01
engagement: Geek-Out
excerpt: Garmin Connect — Bulk Delete Workouts from your Training Library Be very
  careful when you do this as it will also delete the workouts from your...
permalink: blog/articles/2023-01-01-garmin-connect-bulk-delete-workouts-from-your-training-library-25b2991ba2e6
tags:
- garmin
title: Garmin Connect Bulk Delete Workouts From Your Training Library
---
Be very careful when you do this as it will also delete the workouts from your calendar. It will delete all training library workouts. (THIS WILL NOT DELETE COMPLETED ACTIVITIES)

![](https://shared-web.s3.amazonaws.com/blog/images/2024-03-1hL_EcYte2MZU7yoA4AuDiw.png)

What you do is open google chrome, go to the training tab, right click on the page and say inspect, go to console and paste this code. This will delete 1 page of workouts. Sounds complicated, but it’s super simple, just watch the video below.

async function asyncForEach(array, callback) {  
    for (let index = 0; index < array.length; index++) {  
      await callback(array\[index\], index, array);  
    }  
  }

function closePopup(resolve) {  
 document.querySelector('.js-saveBtn').click()

setTimeout(() => {  
    if(!document.querySelector('.js-saveBtn')) {  
     resolve()  
    } else {  
     closePopup(resolve)  
    }  
   }, 250)  
  }

asyncForEach(\[...document.querySelectorAll('.delete-workout')\].map(node => node.getAttribute('data-id')), (id) => {  
   
 const node = document.querySelector(\`.delete-workout\[data-id="${id}"\]\`)  
 node.click()

return new Promise((resolve, reject) => {  
    setTimeout(() => {  
     closePopup(resolve)  
    }, 250)  
   })  
  })

When that page finishes you paste the code one more time.

Below is a quick video showing how to do this.

[YouTube Video](https://www.youtube.com/watch?v=QuRVHsnSVm0)

If you are syncing Coach Jack you might need to remove it from your calendar and add a plan back to your calendar. I said in that video delete everything, but I mean all planned training workouts, not completed activities.
