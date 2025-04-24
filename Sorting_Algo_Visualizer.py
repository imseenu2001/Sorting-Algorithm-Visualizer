from flask import Flask, render_template_string, request, jsonify
import random
import time

app = Flask(__name__)

# Complexity information
complexity_info = {
    'bubble': {'time': 'O(n^2)', 'space': 'O(1)'},
    'insertion': {'time': 'O(n^2)', 'space': 'O(1)'},
    'selection': {'time': 'O(n^2)', 'space': 'O(1)'},
    'quick': {'time': 'O(n log n) average, O(n^2) worst', 'space': 'O(log n)'},
    'merge': {'time': 'O(n log n)', 'space': 'O(n)'},
    'heap': {'time': 'O(n log n)', 'space': 'O(1)'},
    'cycle': {'time': 'O(n^2)', 'space': 'O(1)'},
    'counting': {'time': 'O(n + k)', 'space': 'O(n + k)'},
    'radix': {'time': 'O(d*(n + k))', 'space': 'O(n + k)'},
    'bucket': {'time': 'O(n + k)', 'space': 'O(n + k)'}
}

# HTML template  & grid container for working parallel animations
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
  <title>Sorting Visualizer</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      background: #f2f2f2;
      text-align: center;
    }
    #container {
      width: 90%;
      margin: auto;
    }
    #controls {
      margin-bottom: 20px;
    }
    #visualization {
      margin: 20px auto;
      border: 1px solid #ccc;
      background: #fff;
      padding: 20px;
      display: flex;
      align-items: flex-end;
      justify-content: center;
      height: 300px;
      position: relative;
    }
    #grid-view {
      display: grid;
      grid-template-columns: repeat(5, 1fr);
      grid-gap: 10px;
      margin-top: 20px;
    }
    .grid-cell {
      border: 1px solid #aaa;
      padding: 5px;
      background: #fff;
      position: relative;
      height: 320px;
    }
    .cell-title {
      font-size: 14px;
      font-weight: bold;
      margin-bottom: 5px;
    }
    .cell-visual {
      height: 250px;
      border: 1px solid #ccc;
      display: flex;
      align-items: flex-end;
      justify-content: center;
      position: relative;
      margin-bottom: 5px;
    }
    .cell-stats {
      font-size: 12px;
      color: green;
    }
    .bar-container {
      display: inline-block;
      margin: 0 2px;
      text-align: center;
    }
    .bar {
      width: 20px;
      background-color: blue;
      transition: height 0.2s, background-color 0.2s;
    }
    .bar-label {
      font-size: 10px;
      margin-top: 2px;
    }
    #stats {
      margin-top: 20px;
      font-size: 16px;
      color: green;
    }
    button, select {
      padding: 10px;
      margin: 5px;
    }
  </style>
</head>
<body>
  <div id="container">
    <h1>Sorting Algorithms Visualizer</h1>
    <div id="controls">
      <select id="algorithm">
        <option value="bubble">Bubble Sort</option>
        <option value="insertion">Insertion Sort</option>
        <option value="selection">Selection Sort</option>
        <option value="quick">Quick Sort</option>
        <option value="merge">Merge Sort</option>
        <option value="heap">Heap Sort</option>
        <option value="cycle">Cycle Sort</option>
        <option value="counting">Counting Sort</option>
        <option value="radix">Radix Sort</option>
        <option value="bucket">Bucket Sort</option>
      </select>
      <button onclick="generateNew()">Generate New Array</button>
      <button onclick="startSorting()">Start Sorting</button>
      <button onclick="runAllSorts()">Run All Sorts</button>
    </div>
    <!-- Single sort visualization -->
    <div id="visualization"></div>
    <div id="stats"></div>
    <!-- Grid view for parallel sorting -->
    <div id="grid-view"></div>
  </div>
  <script>
    let array = [];
    let steps = [];
    const delay = 100; // delay between steps in ms
    const scale = 3;   // scaling factor for bar height

    // Generate a new random array and draw in the single visualization
    async function generateNew() {
      const res = await fetch('/generate', { method: 'POST' });
      const data = await res.json();
      array = data.array;
      drawArray(array, document.getElementById('visualization'), []);
      document.getElementById('stats').innerHTML = "";
      // Also clear grid view if present
      document.getElementById('grid-view').innerHTML = "";
    }

    // Run selected sort (single visualization)
    async function startSorting() {
      if (!array || array.length === 0) {
        alert("Please generate an array first!");
        return;
      }
      const algorithm = document.getElementById('algorithm').value;
      const res = await fetch('/sort', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ algorithm: algorithm, array: array })
      });
      const data = await res.json();
      if (data.error) {
        alert("Error: " + data.error);
      } else {
        steps = data.steps;
        animateSteps(steps, document.getElementById('visualization'), document.getElementById('stats'), data.execution_time, data.complexity);
      }
    }

    // Animate steps in the single visualization area
    async function animateSteps(steps, vizContainer, statsContainer, execTime, complexity) {
      for (const step of steps) {
        drawArray(step.array, vizContainer, step.compared);
        await new Promise(resolve => setTimeout(resolve, delay));
      }
      statsContainer.innerHTML = `<strong>Execution Time:</strong> ${execTime.toFixed(4)} seconds<br>
                                  <strong>Time Complexity:</strong> ${complexity.time}<br>
                                  <strong>Space Complexity:</strong> ${complexity.space}`;
    }

    // Draw array as bars inside a given container
    function drawArray(arr, container, compared) {
      container.innerHTML = "";
      arr.forEach((value, index) => {
        const barContainer = document.createElement('div');
        barContainer.classList.add('bar-container');
        const bar = document.createElement('div');
        bar.classList.add("bar");
        bar.style.height = (value * scale) + "px";
        if (compared && compared.includes(index)) {
          bar.style.backgroundColor = "red";
        }
        barContainer.appendChild(bar);
        const label = document.createElement('div');
        label.classList.add("bar-label");
        label.innerText = value;
        barContainer.appendChild(label);
        container.appendChild(barContainer);
      });
    }

    // Run all sorts in parallel in a grid view
    async function runAllSorts() {
      if (!array || array.length === 0) {
        alert("Please generate an array first!");
        return;
      }
      // List of all algorithms
      const algorithms = ["bubble", "insertion", "selection", "quick", "merge", "heap", "cycle", "counting", "radix", "bucket"];
      // Clear grid view container
      const grid = document.getElementById('grid-view');
      grid.innerHTML = "";
      // For each algorithm, create a grid cell
      algorithms.forEach(algo => {
        const cell = document.createElement('div');
        cell.classList.add('grid-cell');
        // Title of algorithm
        const title = document.createElement('div');
        title.classList.add('cell-title');
        title.innerText = algo.charAt(0).toUpperCase() + algo.slice(1) + " Sort";
        cell.appendChild(title);
        // Visualization area
        const cellViz = document.createElement('div');
        cellViz.classList.add('cell-visual');
        cellViz.id = "viz-" + algo;
        cell.appendChild(cellViz);
        // Stats area
        const cellStats = document.createElement('div');
        cellStats.classList.add('cell-stats');
        cellStats.id = "stats-" + algo;
        cell.appendChild(cellStats);
        grid.appendChild(cell);
      });
      // For each algorithm, fetch sort steps and animate in its container (all in parallel)
      algorithms.forEach(async algo => {
        const res = await fetch('/sort', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({ algorithm: algo, array: array })
        });
        const data = await res.json();
        if (!data.error) {
          animateStepsInContainer(data.steps, document.getElementById("viz-" + algo), document.getElementById("stats-" + algo), data.execution_time, data.complexity);
        } else {
          document.getElementById("stats-" + algo).innerText = "Error: " + data.error;
        }
      });
    }

    // Animate steps in a specific grid cell (for each algorithm)
    async function animateStepsInContainer(steps, vizContainer, statsContainer, execTime, complexity) {
      for (const step of steps) {
        drawArray(step.array, vizContainer, step.compared);
        await new Promise(resolve => setTimeout(resolve, delay));
      }
      statsContainer.innerHTML = `<strong>${execTime.toFixed(4)} s</strong><br>
                                  T: ${complexity.time}<br>
                                  S: ${complexity.space}`;
    }

    window.onload = generateNew;
  </script>
</body>
</html>
'''

# Sorting Algorithms code (server side)

def bubble_sort(arr):
    arr = arr.copy()
    steps = []
    n = len(arr)
    for i in range(n):
        for j in range(n - 1):
            swapped = False
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True
            steps.append({'array': arr.copy(), 'compared': [j, j + 1], 'swapped': swapped})
    return steps

def insertion_sort(arr):
    arr = arr.copy()
    steps = []
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0 and key < arr[j]:
            arr[j + 1] = arr[j]
            steps.append({'array': arr.copy(), 'compared': [j, j + 1], 'swapped': True})
            j -= 1
        arr[j + 1] = key
        steps.append({'array': arr.copy(), 'compared': [j + 1, i], 'swapped': True})
    return steps

def selection_sort(arr):
    arr = arr.copy()
    steps = []
    for i in range(len(arr)):
        min_idx = i
        for j in range(i + 1, len(arr)):
            steps.append({'array': arr.copy(), 'compared': [min_idx, j], 'swapped': False})
            if arr[j] < arr[min_idx]:
                min_idx = j
        arr[i], arr[min_idx] = arr[min_idx], arr[i]
        steps.append({'array': arr.copy(), 'compared': [i, min_idx], 'swapped': True})
    return steps

def quick_sort(arr):
    arr = arr.copy()
    steps = []
    def _partition(low, high):
        pivot = arr[high]
        i = low - 1
        for j in range(low, high):
            steps.append({'array': arr.copy(), 'compared': [j, high], 'swapped': False})
            if arr[j] <= pivot:
                i += 1
                arr[i], arr[j] = arr[j], arr[i]
                if i != j:
                    steps.append({'array': arr.copy(), 'compared': [i, j], 'swapped': True})
        arr[i + 1], arr[high] = arr[high], arr[i + 1]
        steps.append({'array': arr.copy(), 'compared': [i + 1, high], 'swapped': True})
        return i + 1
    def _quick_sort(low, high):
        if low < high:
            pi = _partition(low, high)
            _quick_sort(low, pi - 1)
            _quick_sort(pi + 1, high)
    _quick_sort(0, len(arr) - 1)
    return steps

def merge_sort(arr):
    arr = arr.copy()
    steps = []
    def _merge(start, mid, end):
        left = arr[start:mid + 1]
        right = arr[mid + 1:end + 1]
        i = j = 0
        k = start
        while i < len(left) and j < len(right):
            steps.append({'array': arr.copy(), 'compared': [start + i, mid + 1 + j], 'swapped': False})
            if left[i] <= right[j]:
                arr[k] = left[i]
                i += 1
            else:
                arr[k] = right[j]
                j += 1
            k += 1
        while i < len(left):
            arr[k] = left[i]
            steps.append({'array': arr.copy(), 'compared': [k], 'swapped': False})
            i += 1
            k += 1
        while j < len(right):
            arr[k] = right[j]
            steps.append({'array': arr.copy(), 'compared': [k], 'swapped': False})
            j += 1
            k += 1
    def _merge_sort(start, end):
        if start < end:
            mid = (start + end) // 2
            _merge_sort(start, mid)
            _merge_sort(mid + 1, end)
            _merge(start, mid, end)
    _merge_sort(0, len(arr) - 1)
    return steps

def heap_sort(arr):
    arr = arr.copy()
    steps = []
    n = len(arr)
    def heapify(n, i):
        largest = i
        l = 2 * i + 1
        r = 2 * i + 2
        if l < n and arr[l] > arr[largest]:
            largest = l
        if r < n and arr[r] > arr[largest]:
            largest = r
        if largest != i:
            arr[i], arr[largest] = arr[largest], arr[i]
            steps.append({'array': arr.copy(), 'compared': [i, largest], 'swapped': True})
            heapify(n, largest)
    for i in range(n // 2 - 1, -1, -1):
        heapify(n, i)
    for i in range(n - 1, 0, -1):
        arr[i], arr[0] = arr[0], arr[i]
        steps.append({'array': arr.copy(), 'compared': [0, i], 'swapped': True})
        heapify(i, 0)
    return steps

def cycle_sort(arr):
    arr = arr.copy()
    steps = []
    n = len(arr)
    for cycle_start in range(0, n - 1):
        item = arr[cycle_start]
        pos = cycle_start
        for i in range(cycle_start + 1, n):
            steps.append({'array': arr.copy(), 'compared': [cycle_start, i], 'swapped': False})
            if arr[i] < item:
                pos += 1
        if pos == cycle_start:
            continue
        while item == arr[pos]:
            pos += 1
        arr[pos], item = item, arr[pos]
        steps.append({'array': arr.copy(), 'compared': [pos], 'swapped': True})
        while pos != cycle_start:
            pos = cycle_start
            for i in range(cycle_start + 1, n):
                steps.append({'array': arr.copy(), 'compared': [cycle_start, i], 'swapped': False})
                if arr[i] < item:
                    pos += 1
            while item == arr[pos]:
                pos += 1
            arr[pos], item = item, arr[pos]
            steps.append({'array': arr.copy(), 'compared': [pos], 'swapped': True})
    return steps

def counting_sort(arr):
    arr = arr.copy()
    steps = []
    if not arr:
        return steps
    min_val = min(arr)
    max_val = max(arr)
    range_of_elements = max_val - min_val + 1
    count = [0] * range_of_elements
    for num in arr:
        count[num - min_val] += 1
        steps.append({'array': arr.copy(), 'compared': [], 'swapped': False})
    for i in range(1, len(count)):
        count[i] += count[i - 1]
        steps.append({'array': arr.copy(), 'compared': [], 'swapped': False})
    output = [0] * len(arr)
    for i in range(len(arr) - 1, -1, -1):
        output[count[arr[i] - min_val] - 1] = arr[i]
        count[arr[i] - min_val] -= 1
        steps.append({'array': output.copy(), 'compared': [], 'swapped': True})
    return steps

def radix_sort(arr):
    arr = arr.copy()
    steps = []
    def counting_sort_for_radix(arr, exp):
        n = len(arr)
        output = [0] * n
        count = [0] * 10
        for i in range(n):
            index = (arr[i] // exp) % 10
            count[index] += 1
            steps.append({'array': arr.copy(), 'compared': [i], 'swapped': False})
        for i in range(1, 10):
            count[i] += count[i - 1]
            steps.append({'array': arr.copy(), 'compared': [], 'swapped': False})
        for i in range(n - 1, -1, -1):
            index = (arr[i] // exp) % 10
            output[count[index] - 1] = arr[i]
            count[index] -= 1
            steps.append({'array': output.copy(), 'compared': [i], 'swapped': True})
        for i in range(n):
            arr[i] = output[i]
            steps.append({'array': arr.copy(), 'compared': [i], 'swapped': True})
    max_val = max(arr) if arr else 0
    exp = 1
    while max_val // exp > 0:
        counting_sort_for_radix(arr, exp)
        exp *= 10
    return steps

def bucket_sort(arr):
    arr = arr.copy()
    steps = []
    if not arr:
        return steps
    min_val = min(arr)
    max_val = max(arr)
    bucket_count = len(arr)
    buckets = [[] for _ in range(bucket_count)]
    for num in arr:
        index = (num - min_val) * (bucket_count - 1) // (max_val - min_val) if max_val != min_val else 0
        buckets[index].append(num)
        steps.append({'array': arr.copy(), 'compared': [], 'swapped': False})
    sorted_arr = []
    for bucket in buckets:
        bucket.sort()
        sorted_arr.extend(bucket)
        steps.append({'array': sorted_arr.copy(), 'compared': [], 'swapped': True})
    for i in range(len(arr)):
        arr[i] = sorted_arr[i]
        steps.append({'array': arr.copy(), 'compared': [i], 'swapped': True})
    return steps

# Flask Routes

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/sort', methods=['POST'])
def sort_route():
    try:
        data = request.get_json()
        algorithm = data.get('algorithm')
        array = data.get('array')
        if not array or not algorithm:
            return jsonify({'error': 'Missing parameters'}), 400
        start_time = time.perf_counter()
        if algorithm == 'bubble':
            steps = bubble_sort(array)
        elif algorithm == 'insertion':
            steps = insertion_sort(array)
        elif algorithm == 'selection':
            steps = selection_sort(array)
        elif algorithm == 'quick':
            steps = quick_sort(array)
        elif algorithm == 'merge':
            steps = merge_sort(array)
        elif algorithm == 'heap':
            steps = heap_sort(array)
        elif algorithm == 'cycle':
            steps = cycle_sort(array)
        elif algorithm == 'counting':
            steps = counting_sort(array)
        elif algorithm == 'radix':
            steps = radix_sort(array)
        elif algorithm == 'bucket':
            steps = bucket_sort(array)
        else:
            return jsonify({'error': 'Invalid algorithm specified'}), 400
        end_time = time.perf_counter()
        exec_time = end_time - start_time
        complexity = complexity_info.get(algorithm, {})
        return jsonify({'steps': steps, 'execution_time': exec_time, 'complexity': complexity})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/generate', methods=['POST'])
def generate():
    # Generating random array of 10 numbers from 10 and 100.
    return jsonify({'array': [random.randint(10, 100) for _ in range(10)]})

if __name__ == '__main__':
    app.run(debug=True)
