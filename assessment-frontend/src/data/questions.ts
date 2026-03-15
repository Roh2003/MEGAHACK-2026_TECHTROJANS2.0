export interface Question {
  id: number;
  question: string;
  options: string[];
  correctAnswer: number; // index of correct option
}

export const questions: Question[] = [
  {
    id: 1,
    question: "Which of the following best describes Artificial Intelligence?",
    options: [
      "A system that replaces human workers entirely",
      "The simulation of human intelligence by machines",
      "A programming language for robots",
      "A database management system"
    ],
    correctAnswer: 1
  },
  {
    id: 2,
    question: "What does 'Machine Learning' primarily involve?",
    options: [
      "Manually programming every decision rule",
      "Teaching machines to learn from data and improve over time",
      "Building physical robots",
      "Creating user interfaces"
    ],
    correctAnswer: 1
  },
  {
    id: 3,
    question: "Which data structure uses FIFO (First In, First Out) principle?",
    options: [
      "Stack",
      "Queue",
      "Tree",
      "Graph"
    ],
    correctAnswer: 1
  },
  {
    id: 4,
    question: "What is the time complexity of binary search?",
    options: [
      "O(n)",
      "O(n²)",
      "O(log n)",
      "O(1)"
    ],
    correctAnswer: 2
  },
  {
    id: 5,
    question: "In project management, what does 'Agile' methodology emphasize?",
    options: [
      "Rigid planning and documentation",
      "Iterative development and flexibility",
      "Waterfall approach",
      "No planning at all"
    ],
    correctAnswer: 1
  },
  {
    id: 6,
    question: "What is the primary purpose of version control systems like Git?",
    options: [
      "To compile code faster",
      "To track and manage changes to code over time",
      "To design user interfaces",
      "To manage databases"
    ],
    correctAnswer: 1
  },
  {
    id: 7,
    question: "Which of the following is a NoSQL database?",
    options: [
      "MySQL",
      "PostgreSQL",
      "MongoDB",
      "Oracle"
    ],
    correctAnswer: 2
  },
  {
    id: 8,
    question: "What does API stand for?",
    options: [
      "Advanced Programming Interface",
      "Application Programming Interface",
      "Automated Process Integration",
      "Application Process Instruction"
    ],
    correctAnswer: 1
  },
  {
    id: 9,
    question: "Which protocol is primarily used for secure web communication?",
    options: [
      "HTTP",
      "FTP",
      "HTTPS",
      "SMTP"
    ],
    correctAnswer: 2
  },
  {
    id: 10,
    question: "What is the main advantage of cloud computing?",
    options: [
      "It eliminates the need for internet",
      "Scalable resources available on-demand",
      "It only works offline",
      "It requires dedicated hardware at all times"
    ],
    correctAnswer: 1
  },
  {
    id: 11,
    question: "In software development, what does 'CI/CD' stand for?",
    options: [
      "Computer Integration / Computer Delivery",
      "Continuous Integration / Continuous Deployment",
      "Code Inspection / Code Development",
      "Central Intelligence / Central Database"
    ],
    correctAnswer: 1
  },
  {
    id: 12,
    question: "What is the purpose of a firewall in network security?",
    options: [
      "To speed up internet connection",
      "To monitor and control incoming and outgoing network traffic",
      "To store passwords",
      "To compress data"
    ],
    correctAnswer: 1
  }
];
