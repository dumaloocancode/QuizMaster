// Quiz attempts by day
function renderQuizAttemptsByDay(quizResults) {
    // Group attempts by day
    const attemptsByDay = {};
    quizResults.forEach(result => {
      const date = new Date(result.attempt_started_at).toLocaleDateString();
      attemptsByDay[date] = (attemptsByDay[date] || 0) + 1;
    });
    
    // Prepare data for chart
    const labels = Object.keys(attemptsByDay);
    const data = Object.values(attemptsByDay);
    
    const ctx = document.getElementById('quizAttemptsByDay').getContext('2d');
    new Chart(ctx, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [{
          label: 'Quiz Attempts',
          data: data,
          backgroundColor: '#2f5f48',
          borderColor: '#2f5f48',
          borderWidth: 1
        }]
      },
      options: {
        responsive: true,
        scales: {
          y: {
            beginAtZero: true,
            title: {
              display: true,
              text: 'Number of Attempts'
            },
            ticks: {
              stepSize: 1
            }
          },
          x: {
            title: {
              display: true,
              text: 'Date'
            }
          }
        },
        plugins: {
          title: {
            display: true,
            text: 'Quiz Attempts by Day',
            font: {
              size: 16
            }
          }
        }
      }
    });
  }

  
  // Performance review - marks scored every day
function renderDailyPerformance(quizResults) {
    // Group marks by day
    const marksByDay = {};
    const attemptsByDay = {};
    
    quizResults.forEach(result => {
      const date = new Date(result.attempt_started_at).toLocaleDateString();
      if (!marksByDay[date]) {
        marksByDay[date] = 0;
        attemptsByDay[date] = 0;
      }
      marksByDay[date] += result.marks_scored;
      attemptsByDay[date]++;
    });
    
    // Calculate average marks per day
    const avgMarksByDay = {};
    Object.keys(marksByDay).forEach(date => {
      avgMarksByDay[date] = marksByDay[date] / attemptsByDay[date];
    });
    
    // Prepare data for chart
    const labels = Object.keys(avgMarksByDay);
    const data = Object.values(avgMarksByDay);
    
    const ctx = document.getElementById('dailyPerformance').getContext('2d');
    new Chart(ctx, {
      type: 'line',
      data: {
        labels: labels,
        datasets: [{
          label: 'Average Marks',
          data: data,
          backgroundColor: 'rgba(47, 95, 72, 0.2)',
          borderColor: '#2f5f48',
          borderWidth: 2,
          tension: 0.1,
          fill: true
        }]
      },
      options: {
        responsive: true,
        scales: {
          y: {
            beginAtZero: true,
            title: {
              display: true,
              text: 'Average Marks'
            }
          },
          x: {
            title: {
              display: true,
              text: 'Date'
            }
          }
        },
        plugins: {
          title: {
            display: true,
            text: 'Daily Performance Review',
            font: {
              size: 16
            }
          }
        }
      }
    });
  }

  // Chapter-wise marks scored
function renderChapterPerformance(quizResults) {
    // Group marks by chapter
    const marksByChapter = {};
    const attemptsByChapter = {};
    
    quizResults.forEach(result => {
      const chapter = result.quiz.chapter.name;
      const subject = result.quiz.chapter.subject.name;
      const chapterKey = `${subject}: ${chapter}`;
      
      if (!marksByChapter[chapterKey]) {
        marksByChapter[chapterKey] = 0;
        attemptsByChapter[chapterKey] = 0;
      }
      marksByChapter[chapterKey] += result.marks_scored;
      attemptsByChapter[chapterKey]++;
    });
    
    // Calculate average marks per chapter
    const avgMarksByChapter = {};
    Object.keys(marksByChapter).forEach(chapter => {
      avgMarksByChapter[chapter] = marksByChapter[chapter] / attemptsByChapter[chapter];
    });
    
    // Prepare data for chart
    const labels = Object.keys(avgMarksByChapter);
    const data = Object.values(avgMarksByChapter);
    
    const ctx = document.getElementById('chapterPerformance').getContext('2d');
    new Chart(ctx, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [{
          label: 'Average Marks',
          data: data,
          backgroundColor: 'rgba(47, 95, 72, 0.7)',
          borderColor: 'rgb(47, 95, 72)',
          borderWidth: 1
        }]
      },
      options: {
        responsive: true,
        indexAxis: 'y',  // Horizontal bar chart for better readability with many chapters
        scales: {
          x: {
            beginAtZero: true,
            title: {
              display: true,
              text: 'Average Marks'
            }
          },
          y: {
            title: {
              display: true,
              text: 'Chapter'
            }
          }
        },
        plugins: {
          title: {
            display: true,
            text: 'Performance by Chapter',
            font: {
              size: 16
            }
          }
        }
      }
    });
  }

  // Subject-wise marks scored
function renderSubjectPerformance(quizResults) {
    // Group marks by subject
    const marksBySubject = {};
    const attemptsBySubject = {};
    
    quizResults.forEach(result => {
      const subject = result.quiz.chapter.subject.name;
      if (!marksBySubject[subject]) {
        marksBySubject[subject] = 0;
        attemptsBySubject[subject] = 0;
      }
      marksBySubject[subject] += result.marks_scored;
      attemptsBySubject[subject]++;
    });
    
    // Calculate average marks per subject
    const avgMarksBySubject = {};
    Object.keys(marksBySubject).forEach(subject => {
      avgMarksBySubject[subject] = marksBySubject[subject] / attemptsBySubject[subject];
    });
    
    // Prepare data for chart
    const labels = Object.keys(avgMarksBySubject);
    const data = Object.values(avgMarksBySubject);
    
    const ctx = document.getElementById('subjectPerformance').getContext('2d');
    new Chart(ctx, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [{
          label: 'Average Marks',
          data: data,
          backgroundColor: [
            'rgba(47, 95, 72, 0.7)',
            'rgba(75, 192, 192, 0.7)',
            'rgba(153, 102, 255, 0.7)',
            'rgba(255, 159, 64, 0.7)'
          ],
          borderColor: [
            'rgb(47, 95, 72)',
            'rgb(75, 192, 192)',
            'rgb(153, 102, 255)',
            'rgb(255, 159, 64)'
          ],
          borderWidth: 1
        }]
      },
      options: {
        responsive: true,
        scales: {
          y: {
            beginAtZero: true,
            title: {
              display: true,
              text: 'Average Marks'
            }
          },
          x: {
            title: {
              display: true,
              text: 'Subject'
            }
          }
        },
        plugins: {
          title: {
            display: true,
            text: 'Performance by Subject',
            font: {
              size: 16
            }
          }
        }
      }
    });
  }
  