<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="bg-gradient-to-r from-blue-600 to-blue-400 rounded-lg shadow-lg p-6 text-white">
      <h1 class="text-3xl font-bold mb-2">📊 สรุปผลการมาเรียน</h1>
      <p class="text-blue-100">ภาพรวมการเข้าเรียนของนักเรียนทั้งหมด</p>
    </div>

    <!-- Date Selector -->
    <div class="bg-white rounded-lg shadow-lg p-4">
      <div class="flex items-center justify-between flex-wrap gap-4">
        <div class="flex items-center space-x-4">
          <label class="font-medium text-gray-700">เลือกวันที่:</label>
          <input 
            type="date" 
            v-model="selectedDate"
            @change="loadAttendanceData"
            class="px-4 py-2 border border-blue-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button 
            @click="setToday"
            class="px-4 py-2 bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 transition-colors"
          >
            วันนี้
          </button>
        </div>
        <div class="text-sm text-gray-600">
          อัพเดทล่าสุด: {{ lastUpdate }}
        </div>
      </div>
    </div>

    <!-- Summary Stats -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div class="bg-white rounded-lg shadow-lg p-6 border-l-4 border-blue-500">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-gray-600 text-sm font-medium">นักเรียนทั้งหมด</p>
            <p class="text-3xl font-bold text-gray-900 mt-2">{{ totalStudents }}</p>
          </div>
          <div class="bg-blue-100 rounded-full p-3">
            <Users size="24" class="text-blue-600" />
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg shadow-lg p-6 border-l-4 border-green-500">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-gray-600 text-sm font-medium">มาเรียน</p>
            <p class="text-3xl font-bold text-green-600 mt-2">{{ presentCount }}</p>
            <p class="text-sm text-gray-500">{{ presentPercentage }}%</p>
          </div>
          <div class="bg-green-100 rounded-full p-3">
            <UserCheck size="24" class="text-green-600" />
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg shadow-lg p-6 border-l-4 border-red-500">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-gray-600 text-sm font-medium">ขาดเรียน</p>
            <p class="text-3xl font-bold text-red-600 mt-2">{{ absentCount }}</p>
            <p class="text-sm text-gray-500">{{ absentPercentage }}%</p>
          </div>
          <div class="bg-red-100 rounded-full p-3">
            <UserX size="24" class="text-red-600" />
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg shadow-lg p-6 border-l-4 border-purple-500">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-gray-600 text-sm font-medium">การเช็คชื่อทั้งหมด</p>
            <p class="text-3xl font-bold text-purple-600 mt-2">{{ totalCheckIns }}</p>
            <p class="text-sm text-gray-500">{{ totalCheckIns }} ครั้ง</p>
          </div>
          <div class="bg-purple-100 rounded-full p-3">
            <Camera size="24" class="text-purple-600" />
          </div>
        </div>
      </div>
    </div>

    <!-- Student List -->
    <div class="bg-white rounded-lg shadow-lg overflow-hidden">
      <div class="p-4 border-b border-gray-200 flex items-center justify-between">
        <h2 class="text-lg font-bold text-blue-900 flex items-center">
          <ClipboardList size="20" class="mr-2" />
          รายชื่อนักเรียน - {{ formatDate(selectedDate) }}
        </h2>
        <button 
          @click="loadAttendanceData"
          class="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          title="รีเฟรช"
        >
          <RefreshCw size="20" :class="{ 'animate-spin': loading }" />
        </button>
      </div>

      <div class="overflow-x-auto">
        <table class="w-full">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">ลำดับ</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">ชื่อ</th>
              <th class="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase">สถานะ</th>
              <th class="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase">เวลาล่าสุด</th>
              <th class="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase">จำนวนครั้ง</th>
              <th class="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase">วิธีการ</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200">
            <tr v-for="(student, index) in studentsData" :key="student.name" class="hover:bg-gray-50">
              <td class="px-4 py-3 text-sm text-gray-500">{{ index + 1 }}</td>
              <td class="px-4 py-3">
                <div class="flex items-center">
                  <div class="w-10 h-10 rounded-full flex items-center justify-center text-white font-bold mr-3"
                       :class="student.present ? 'bg-green-500' : 'bg-gray-400'">
                    {{ student.name.charAt(0).toUpperCase() }}
                  </div>
                  <span class="font-medium text-gray-900">{{ student.name }}</span>
                </div>
              </td>
              <td class="px-4 py-3 text-center">
                <span v-if="student.present" 
                      class="px-3 py-1 rounded-full text-xs font-medium bg-green-100 text-green-700">
                  ✓ มาเรียน
                </span>
                <span v-else 
                      class="px-3 py-1 rounded-full text-xs font-medium bg-red-100 text-red-700">
                  ✗ ขาดเรียน
                </span>
              </td>
              <td class="px-4 py-3 text-center text-sm text-gray-600">
                {{ student.checkTime || '-' }}
              </td>
              <td class="px-4 py-3 text-center">
                <span v-if="student.present" class="px-2 py-1 bg-blue-100 text-blue-700 rounded-full text-xs font-medium">
                  {{ student.checkCount || 1 }} ครั้ง
                </span>
                <span v-else class="text-gray-400">-</span>
              </td>
              <td class="px-4 py-3 text-center">
                <span v-if="student.present" 
                      class="px-2 py-1 rounded-full text-xs font-medium"
                      :class="student.checkedByCamera ? 'bg-purple-100 text-purple-700' : 'bg-blue-100 text-blue-700'">
                  {{ student.checkedByCamera ? '📷 กล้อง' : '✋ Manual' }}
                </span>
                <span v-else class="text-gray-400">-</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-if="studentsData.length === 0 && !loading" class="p-8 text-center text-gray-500">
        <ClipboardList size="48" class="mx-auto mb-2 opacity-50" />
        <p>ไม่พบข้อมูลนักเรียน</p>
        <p class="text-sm">กรุณาตรวจสอบไฟล์ label_map.json</p>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="bg-white rounded-lg shadow-lg p-6">
      <h3 class="text-lg font-bold text-blue-900 mb-4 flex items-center">
        <Zap size="20" class="mr-2" />
        การดำเนินการ
      </h3>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <NuxtLink to="/" 
                  class="flex items-center justify-center p-4 bg-green-50 border border-green-200 rounded-lg hover:bg-green-100 transition-colors group">
          <ClipboardCheck size="20" class="text-green-600 mr-2" />
          <span class="font-medium text-green-700 group-hover:text-green-800">เช็คชื่อใหม่</span>
        </NuxtLink>
        
        <NuxtLink to="/history-edit" 
                  class="flex items-center justify-center p-4 bg-blue-50 border border-blue-200 rounded-lg hover:bg-blue-100 transition-colors group">
          <FileEdit size="20" class="text-blue-600 mr-2" />
          <span class="font-medium text-blue-700 group-hover:text-blue-800">แก้ไขประวัติ</span>
        </NuxtLink>
        
        <NuxtLink to="/students-new" 
                  class="flex items-center justify-center p-4 bg-purple-50 border border-purple-200 rounded-lg hover:bg-purple-100 transition-colors group">
          <Users size="20" class="text-purple-600 mr-2" />
          <span class="font-medium text-purple-700 group-hover:text-purple-800">รายชื่อนักเรียน</span>
        </NuxtLink>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Users, UserCheck, UserX, Camera, ClipboardList, RefreshCw, ClipboardCheck, FileEdit, Zap } from 'lucide-vue-next'

const config = useRuntimeConfig()

// State
const selectedDate = ref(new Date().toISOString().split('T')[0])
const studentsData = ref([])
const attendanceRecords = ref([])
const loading = ref(false)
const lastUpdate = ref('')

// Computed
const totalStudents = computed(() => studentsData.value.length)
const presentCount = computed(() => studentsData.value.filter(s => s.present).length)
const absentCount = computed(() => studentsData.value.filter(s => !s.present).length)
const totalCheckIns = computed(() => attendanceRecords.value.length)

const presentPercentage = computed(() => {
  if (totalStudents.value === 0) return 0
  return Math.round((presentCount.value / totalStudents.value) * 100)
})

const absentPercentage = computed(() => {
  if (totalStudents.value === 0) return 0
  return Math.round((absentCount.value / totalStudents.value) * 100)
})

// Methods
const setToday = () => {
  selectedDate.value = new Date().toISOString().split('T')[0]
  loadAttendanceData()
}

const loadAttendanceData = async () => {
  loading.value = true
  try {
    // Load students status
    const statusResponse = await $fetch(`${config.public.apiBase}/api/v1/attendance/students-status?date=${selectedDate.value}`)
    if (statusResponse.success) {
      // Load attendance records for the date to get time and method info
      const recordsResponse = await $fetch(`${config.public.apiBase}/api/v1/attendance/by-date/${selectedDate.value}`)
      const records = recordsResponse.success ? recordsResponse.data : []
      
      // Store all attendance records for counting
      attendanceRecords.value = records
      
      // Combine data - show latest check-in time for each student
      studentsData.value = statusResponse.data.map(student => {
        const studentRecords = records.filter(r => r.name === student.name)
        const latestRecord = studentRecords.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))[0]
        
        return {
          ...student,
          checkTime: latestRecord ? formatTime(latestRecord.timestamp) : null,
          checkedByCamera: latestRecord ? latestRecord.camera_id !== 'manual' : false,
          checkCount: studentRecords.length // Show how many times they checked in
        }
      })
    }
    
    lastUpdate.value = new Date().toLocaleTimeString('th-TH')
  } catch (error) {
    console.error('Error loading attendance data:', error)
  } finally {
    loading.value = false
  }
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('th-TH', { 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric' 
  })
}

const formatTime = (timestamp) => {
  if (!timestamp) return '-'
  const date = new Date(timestamp)
  return date.toLocaleTimeString('th-TH', { hour: '2-digit', minute: '2-digit' })
}

// Lifecycle
onMounted(() => {
  loadAttendanceData()
  
  // Auto refresh every 30 seconds
  setInterval(() => {
    loadAttendanceData()
  }, 30000)
})
</script>
