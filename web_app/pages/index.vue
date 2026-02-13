<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="bg-gradient-to-r from-blue-600 to-blue-400 rounded-lg shadow-lg p-6 text-white">
      <h1 class="text-3xl font-bold mb-2">📋 ระบบเช็คชื่อนักเรียน</h1>
      <p class="text-blue-100">ระบบเช็คชื่อนักเรียนด้วยกล้อง พร้อมแก้ไขแบบ Manual</p>
    </div>

    <!-- Date Selector -->
    <div class="bg-white rounded-lg shadow-lg p-4">
      <div class="flex items-center justify-between flex-wrap gap-4">
        <div class="flex items-center space-x-4">
          <label class="font-medium text-gray-700">วันที่เวลาปัจจุบัน:</label>
          <span class="font-medium text-blue-700">{{ currentDateTime }}</span>
        </div>
        <div class="flex items-center space-x-2 text-sm text-gray-600">
          <span class="px-3 py-1 bg-green-100 text-green-700 rounded-full">
            มา: {{ presentCount }}
          </span>
          <span class="px-3 py-1 bg-red-100 text-red-700 rounded-full">
            ขาด: {{ absentCount }}
          </span>
          <span class="px-3 py-1 bg-blue-100 text-blue-700 rounded-full">
            ทั้งหมด: {{ totalStudents }}
          </span>
        </div>
      </div>
    </div>

    <!-- Main Content: Camera Section -->
    <div class="bg-white rounded-lg shadow-lg p-6">
      <h2 class="text-xl font-bold mb-4 flex items-center text-blue-900">
        <Camera class="mr-2" size="24" />
        กล้องตรวจจับใบหน้า
      </h2>
      
      <!-- Video Display -->
      <div class="relative bg-gray-900 rounded-lg overflow-hidden" style="padding-bottom: 56.25%;">
        <img 
          v-if="streamImage" 
          :src="`data:image/jpeg;base64,${streamImage}`" 
          alt="Stream"
          class="absolute inset-0 w-full h-full object-contain"
        />
        <div v-else class="absolute inset-0 flex items-center justify-center">
          <div class="text-white text-center">
            <CameraOff size="48" class="mx-auto mb-2 opacity-50" />
            <p>รอสัญญาณจากกล้อง...</p>
            <p class="text-sm text-gray-400 mt-2">กรุณาเริ่ม Detection Program</p>
          </div>
        </div>
      </div>
      
      <!-- Detection Stats -->
      <div class="mt-6 grid grid-cols-3 gap-4">
        <div class="bg-blue-50 rounded-lg p-4 text-center border border-blue-200">
          <p class="text-sm text-gray-600 font-medium">ตรวจจับได้</p>
          <p class="text-3xl font-bold text-blue-600">{{ detectedFaces.length }}</p>
        </div>
        <div class="bg-green-50 rounded-lg p-4 text-center border border-green-200">
          <p class="text-sm text-gray-600 font-medium">รู้จัก</p>
          <p class="text-3xl font-bold text-green-600">{{ knownFaces.length }}</p>
        </div>
        <div class="bg-orange-50 rounded-lg p-4 text-center border border-orange-200">
          <p class="text-sm text-gray-600 font-medium">ไม่รู้จัก</p>
          <p class="text-3xl font-bold text-orange-600">{{ unknownCount }}</p>
        </div>
      </div>

      <!-- Detected Faces List -->
      <div class="mt-6 bg-gray-50 rounded-lg p-4">
        <h3 class="font-semibold mb-4 text-gray-700 text-lg">ใบหน้าที่ตรวจจับได้:</h3>
        <div v-if="knownFaces.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          <div v-for="face in knownFaces" 
               :key="face.name"
               class="flex items-center justify-between bg-white rounded-lg p-3 border border-green-200 shadow-sm">
            <div class="flex items-center">
              <div class="w-10 h-10 bg-green-500 rounded-full flex items-center justify-center text-white font-bold mr-3">
                {{ face.name.charAt(0).toUpperCase() }}
              </div>
              <span class="font-medium">{{ face.name }}</span>
            </div>
            <span class="text-sm text-green-600 font-medium">{{ (face.confidence * 100).toFixed(0) }}%</span>
          </div>
        </div>
        <div v-else class="text-center py-8 text-gray-500">
          <Users size="48" class="mx-auto mb-2 opacity-50" />
          <p class="text-lg">ยังไม่มีใบหน้าที่ตรวจจับได้</p>
          <p class="text-sm mt-1">รอให้กล้องตรวจจับใบหน้า</p>
        </div>
      </div>

      <!-- Check Attendance Button -->
      <button 
        @click="checkAttendanceFromCamera"
        :disabled="knownFaces.length === 0 || checkingAttendance"
        class="w-full mt-6 py-4 bg-gradient-to-r from-green-500 to-green-600 text-white font-bold text-lg rounded-lg hover:from-green-600 hover:to-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg hover:shadow-xl"
      >
        <span v-if="checkingAttendance" class="flex items-center justify-center">
          <RefreshCw class="animate-spin mr-2" size="20" />
          กำลังบันทึก...
        </span>
        <span v-else class="flex items-center justify-center">
          <CheckCircle class="mr-2" size="24" />
          เช็คชื่อจากกล้อง ({{ knownFaces.length }} คน)
        </span>
      </button>
    </div>

    <!-- Attendance Summary Popup -->
    <div v-if="showSummaryModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden">
        <!-- Header -->
        <div class="bg-gradient-to-r from-blue-600 to-blue-400 p-6 text-white">
          <div class="flex items-center justify-between">
            <div class="flex items-center">
              <div class="w-12 h-12 bg-white bg-opacity-20 rounded-full flex items-center justify-center mr-4">
                <CheckCircle class="w-6 h-6 text-white" />
              </div>
              <div>
                <h3 class="text-xl font-bold">📋 เช็คชื่อนักเรียน</h3>
                <p class="text-blue-100 text-sm">ตรวจสอบและแก้ไขก่อนบันทึก</p>
              </div>
            </div>
            <button 
              @click="cancelAttendanceCheck"
              class="p-2 hover:bg-white hover:bg-opacity-20 rounded-lg transition-colors"
            >
              <X class="w-5 h-5 text-white" />
            </button>
          </div>
        </div>

        <!-- Content -->
        <div class="p-6 overflow-y-auto max-h-[calc(90vh-200px)]">
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <!-- Left Column: Detection Summary -->
            <div class="space-y-4">
              <!-- Date and Time -->
              <div class="bg-blue-50 rounded-lg p-4 border border-blue-200">
                <h4 class="font-medium text-blue-900 mb-3">📅 ข้อมูลการเช็คชื่อ</h4>
                <div class="space-y-2">
                  <div class="flex items-center justify-between">
                    <span class="text-sm font-medium text-blue-900">วันที่:</span>
                    <span class="text-sm text-blue-700">{{ formatDate(selectedDate) }}</span>
                  </div>
                  <div class="flex items-center justify-between">
                    <span class="text-sm font-medium text-blue-900">เวลา:</span>
                    <span class="text-sm text-blue-700">{{ currentTime }}</span>
                  </div>
                </div>
              </div>

              <!-- Detected Students -->
              <div class="bg-green-50 rounded-lg p-4 border border-green-200">
                <h4 class="font-medium text-green-900 mb-3">👥 นักเรียนที่ตรวจจับได้จากกล้อง</h4>
                <div v-if="detectedStudentsForSummary.length > 0" class="space-y-2 max-h-40 overflow-y-auto">
                  <div v-for="student in detectedStudentsForSummary" :key="student.name"
                       class="flex items-center justify-between p-2 bg-white rounded border">
                    <div class="flex items-center">
                      <div class="w-6 h-6 bg-green-500 rounded-full flex items-center justify-center text-white font-bold text-xs mr-2">
                        {{ student.name.charAt(0).toUpperCase() }}
                      </div>
                      <span class="font-medium text-sm">{{ student.name }}</span>
                    </div>
                    <span class="text-xs text-green-600 font-medium">{{ (student.confidence * 100).toFixed(0) }}%</span>
                  </div>
                </div>
                <div v-else class="text-center py-4">
                  <Users class="w-8 h-8 text-gray-400 mx-auto mb-2" />
                  <p class="text-gray-500 text-sm">ไม่พบนักเรียนที่ตรวจจับได้</p>
                </div>
              </div>

              <!-- Already Checked Warning -->
              <div v-if="alreadyCheckedStudents.length > 0" class="bg-yellow-50 rounded-lg p-4 border border-yellow-200">
                <h4 class="font-medium text-yellow-800 mb-2">⚠️ เช็คชื่อแล้ววันนี้:</h4>
                <div class="space-y-1">
                  <div v-for="name in alreadyCheckedStudents" :key="name" class="text-sm text-yellow-700">
                    • {{ name }}
                  </div>
                </div>
              </div>
            </div>

            <!-- Right Column: Manual Student List -->
            <div class="space-y-4">
              <div class="bg-gray-50 rounded-lg p-4 border border-gray-200">
                <div class="flex items-center justify-between mb-3">
                  <h4 class="font-medium text-gray-900">✏️ แก้ไขการเช็คชื่อแบบ Manual</h4>
                  <div class="text-xs text-gray-500">
                    มา: {{ presentCount }} | ขาด: {{ absentCount }}
                  </div>
                </div>

                <!-- Student List with Toggles -->
                <div class="space-y-2 max-h-80 overflow-y-auto">
                  <div v-for="student in studentsStatus" 
                       :key="student.name"
                       class="flex items-center justify-between p-2 rounded border transition-all"
                       :class="student.present ? 'bg-green-50 border-green-300' : 'bg-red-50 border-red-300'">
                    <div class="flex items-center">
                      <div class="w-6 h-6 rounded-full flex items-center justify-center text-white font-bold text-xs mr-2"
                           :class="student.present ? 'bg-green-500' : 'bg-red-400'">
                        {{ student.name.charAt(0).toUpperCase() }}
                      </div>
                      <div>
                        <p class="font-medium text-sm">{{ student.name }}</p>
                        <p class="text-xs text-gray-500">
                          <span v-if="student.checked_by_camera" class="text-green-600">📷 กล้อง</span>
                          <span v-else-if="student.present" class="text-blue-600">✋ Manual</span>
                          <span v-else class="text-red-500">✗ ขาด</span>
                        </p>
                      </div>
                    </div>
                    
                    <!-- Toggle Switch -->
                    <label class="relative inline-flex items-center cursor-pointer">
                      <input 
                        type="checkbox" 
                        v-model="student.present"
                        @change="markAsModified"
                        class="sr-only peer"
                      />
                      <div class="w-10 h-5 bg-red-300 peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-0.5 after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-green-500"></div>
                      <span class="ml-2 text-xs font-medium" :class="student.present ? 'text-green-700' : 'text-red-700'">
                        {{ student.present ? 'มา' : 'ขาด' }}
                      </span>
                    </label>
                  </div>
                  
                  <div v-if="studentsStatus.length === 0" class="text-center py-8 text-gray-500">
                    <Users size="32" class="mx-auto mb-2 opacity-50" />
                    <p class="text-sm">ไม่พบข้อมูลนักเรียน</p>
                  </div>
                </div>

                <!-- Modification Warning -->
                <div v-if="hasModifications" class="mt-3 p-2 bg-orange-50 border border-orange-200 rounded text-center">
                  <p class="text-xs text-orange-600">⚠️ มีการแก้ไขที่ยังไม่ได้บันทึก</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Footer Actions -->
        <div class="bg-gray-50 px-6 py-4 border-t border-gray-200">
          <div class="flex items-center justify-between">
            <div class="text-sm text-gray-600">
              จะบันทึก: <span class="font-medium text-green-600">{{ presentCount }} คน</span>
            </div>
            <div class="flex space-x-3">
              <button 
                @click="cancelAttendanceCheck"
                class="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors font-medium"
              >
                ยกเลิก
              </button>
              <button 
                @click="confirmAttendanceCheck"
                :disabled="confirmingAttendance"
                class="px-6 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 disabled:opacity-50 transition-colors font-medium"
              >
                <span v-if="confirmingAttendance" class="flex items-center">
                  <RefreshCw class="animate-spin mr-2" size="16" />
                  กำลังบันทึก...
                </span>
                <span v-else class="flex items-center">
                  <Save class="mr-2" size="16" />
                  บันทึกการเช็คชื่อ
                </span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Success/Error Messages -->
    <div v-if="message" 
         class="fixed bottom-4 right-4 px-6 py-4 rounded-lg shadow-lg text-white z-50"
         :class="messageType === 'success' ? 'bg-green-500' : 'bg-red-500'">
      {{ message }}
    </div>
  </div>
</template>

<script setup>
import { Camera, CameraOff, Users, CheckCircle, RefreshCw, Save, Zap, BarChart3, FileEdit, X } from 'lucide-vue-next'

const config = useRuntimeConfig()

// State
const selectedDate = ref(new Date().toISOString().split('T')[0])
const studentsStatus = ref([])
const loading = ref(false)
const saving = ref(false)
const checkingAttendance = ref(false)
const hasModifications = ref(false)
const message = ref('')
const messageType = ref('success')
const currentDateTime = ref('')

// Camera state
const streamImage = ref(null)
const detectedFaces = ref([])
const knownFaces = ref([])
const unknownCount = ref(0)
let ws = null

// Popup state
const showSummaryModal = ref(false)
const detectedStudentsForSummary = ref([])
const alreadyCheckedStudents = ref([])
const confirmingAttendance = ref(false)
const currentTime = ref('')

// Computed
const totalStudents = computed(() => studentsStatus.value.length)
const presentCount = computed(() => studentsStatus.value.filter(s => s.present).length)
const absentCount = computed(() => studentsStatus.value.filter(s => !s.present).length)

// Methods
const setToday = () => {
  selectedDate.value = new Date().toISOString().split('T')[0]
  loadAttendanceStatus()
}

const loadAttendanceStatus = async () => {
  loading.value = true
  try {
    const response = await $fetch(`${config.public.apiBase}/api/v1/attendance/students-status?date=${selectedDate.value}`)
    if (response.success) {
      studentsStatus.value = response.data
      hasModifications.value = false
    }
  } catch (error) {
    console.error('Error loading attendance status:', error)
    showMessage('ไม่สามารถโหลดข้อมูลได้', 'error')
  } finally {
    loading.value = false
  }
}

const markAsModified = () => {
  hasModifications.value = true
}

const saveManualAttendance = async () => {
  saving.value = true
  try {
    const response = await $fetch(`${config.public.apiBase}/api/v1/attendance/manual-save`, {
      method: 'POST',
      body: {
        date: selectedDate.value,
        students: studentsStatus.value.map(s => ({
          name: s.name,
          present: s.present
        }))
      }
    })
    
    if (response.success) {
      hasModifications.value = false
      showMessage(`บันทึกสำเร็จ! (เพิ่ม ${response.saved_count}, ลบ ${response.removed_count})`, 'success')
      await loadAttendanceStatus()
    }
  } catch (error) {
    console.error('Error saving attendance:', error)
    showMessage('ไม่สามารถบันทึกได้', 'error')
  } finally {
    saving.value = false
  }
}

const checkAttendanceFromCamera = async () => {
  if (knownFaces.value.length === 0) {
    showMessage('ไม่พบใบหน้าที่ตรวจจับได้', 'error')
    return
  }
  
  // Show summary popup instead of immediate save
  detectedStudentsForSummary.value = [...knownFaces.value]
  currentTime.value = new Date().toLocaleTimeString('th-TH')
  
  // Check which students are already checked in today
  try {
    const response = await $fetch(`${config.public.apiBase}/api/v1/attendance/students-status?date=${selectedDate.value}`)
    if (response.success) {
      const checkedStudents = response.data.filter(s => s.present).map(s => s.name)
      alreadyCheckedStudents.value = knownFaces.value
        .map(f => f.name)
        .filter(name => checkedStudents.includes(name))
    }
  } catch (error) {
    console.error('Error checking existing attendance:', error)
    alreadyCheckedStudents.value = []
  }
  
  showSummaryModal.value = true
}

const confirmAttendanceCheck = async () => {
  if (detectedStudentsForSummary.value.length === 0) {
    showMessage('ไม่มีนักเรียนที่จะบันทึก', 'error')
    showSummaryModal.value = false
    return
  }
  
  confirmingAttendance.value = true
  try {
    const response = await $fetch(`${config.public.apiBase}/api/v1/attendance/check`, {
      method: 'POST',
      body: {
        known_faces: detectedStudentsForSummary.value,
        camera_id: 'camera_0',
        timestamp: new Date().toISOString()
      }
    })
    
    if (response.status === 'success') {
      showSummaryModal.value = false
      showMessage(`เช็คชื่อสำเร็จ! ${response.saved_names.join(', ')}`, 'success')
      await loadAttendanceStatus()
      
      // Navigate to dashboard after successful save
      setTimeout(() => {
        navigateTo('/dashboard')
      }, 1500)
    }
  } catch (error) {
    console.error('Error confirming attendance:', error)
    showMessage('ไม่สามารถบันทึกการเช็คชื่อได้', 'error')
  } finally {
    confirmingAttendance.value = false
  }
}

const cancelAttendanceCheck = () => {
  showSummaryModal.value = false
  detectedStudentsForSummary.value = []
  alreadyCheckedStudents.value = []
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('th-TH', { 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric' 
  })
}

const showMessage = (msg, type = 'success') => {
  message.value = msg
  messageType.value = type
  setTimeout(() => {
    message.value = ''
  }, 3000)
}

const connectWebSocket = () => {
  const wsUrl = config.public.wsUrl || 'ws://localhost:8000/ws'
  ws = new WebSocket(wsUrl)
  
  ws.onopen = () => {
    console.log('✅ WebSocket connected')
  }
  
  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data)
      
      if (data.type === 'detection' && data.payload) {
        streamImage.value = data.payload.stream_image
        detectedFaces.value = data.payload.known_faces || []
        knownFaces.value = (data.payload.known_faces || []).filter(f => f.name !== 'Unknown')
        unknownCount.value = data.payload.unknown_faces || 0
      }
      
      if (data.type === 'attendance_checked' || data.type === 'attendance_manual_updated') {
        loadAttendanceStatus()
      }
    } catch (error) {
      console.error('WebSocket message error:', error)
    }
  }
  
  ws.onerror = (error) => {
    console.error('WebSocket error:', error)
  }
  
  ws.onclose = () => {
    console.log('WebSocket disconnected, reconnecting...')
    setTimeout(connectWebSocket, 3000)
  }
}

// Update current date time
const updateCurrentDateTime = () => {
  const now = new Date()
  currentDateTime.value = now.toLocaleString('th-TH', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

// Lifecycle
onMounted(() => {
  loadAttendanceStatus()
  connectWebSocket()
  
  // Update current date time immediately and every second
  updateCurrentDateTime()
  setInterval(updateCurrentDateTime, 1000)
})

onUnmounted(() => {
  if (ws) {
    ws.close()
  }
})
</script>

<style scoped>
/* Custom scrollbar */
::-webkit-scrollbar {
  width: 6px;
}
::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}
::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}
::-webkit-scrollbar-thumb:hover {
  background: #a1a1a1;
}
</style>
