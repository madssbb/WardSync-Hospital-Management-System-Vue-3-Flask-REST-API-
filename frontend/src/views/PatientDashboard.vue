<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const appointments = ref([])
const doctors = ref([])
const specs = ref([])
const searchQ = ref('')
const selectedSpec = ref('')
const selectedDoctor = ref(null)
const selectedSlot = ref(null)
const selectedTreatment = ref(null)
const rescheduleApp = ref(null)
const rescheduleSlot = ref(null)
const checkoutStep = ref(1)
const selectedFile = ref(null)
const statusMsg = ref({ text: '', type: '' })

// Profile
const profile = ref({ name: '', email: '', contact: '', dob: '', username: '' })
const profileForm = ref({ name: '', email: '', contact: '', dob: '', password: '' })
const currentView = ref('appointments') // 'appointments' | 'profile'

const fetchData = async () => {
    // Fetch appointments and specs independently so one failure doesn't block the other
    try {
        const appRes = await axios.get('/api/patient/appointments')
        appointments.value = appRes.data
    } catch (err) {
        console.error('Failed to fetch appointments', err)
    }
    try {
        const specRes = await axios.get('/api/patient/specializations')
        specs.value = specRes.data
    } catch (err) {
        console.error('Failed to fetch specializations', err)
    }
}

const fetchProfile = async () => {
    try {
        const res = await axios.get('/api/patient/profile')
        profile.value = res.data
        profileForm.value = { name: res.data.name, email: res.data.email, contact: res.data.contact || '', dob: res.data.dob || '', password: '' }
    } catch (err) {
        console.error('Failed to fetch profile', err)
    }
}

const handleFileUpload = (event) => {
    const file = event.target.files[0]
    if (file) {
        selectedFile.value = file
    }
}

const saveProfile = async () => {
    try {
        // First handle normal profile update
        const payload = { ...profileForm.value }
        if (!payload.password) delete payload.password
        await axios.put('/api/patient/profile', payload)
        
        // Then handle file upload if exists
        if (selectedFile.value) {
            const formData = new FormData()
            formData.append('file', selectedFile.value)
            await axios.post('/api/patient/upload-document', formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            })
            selectedFile.value = null
        }
        
        await fetchProfile()
        showMsg('Profile updated successfully')
    } catch (err) {
        showMsg(err.response?.data?.msg || 'Update failed', 'danger')
    }
}

const showMsg = (text, type = 'success') => {
    statusMsg.value = { text, type }
    setTimeout(() => { statusMsg.value = { text: '', type: '' } }, 4000)
}

const searchDoctors = async () => {
    const res = await axios.get('/api/patient/doctors', {
        params: { q: searchQ.value, specialization_id: selectedSpec.value }
    })
    doctors.value = res.data
}

onMounted(() => {
    fetchData()
    fetchProfile()
})

const startBooking = () => {
    doctors.value = []
    checkoutStep.value = 1
    searchDoctors()
}

const selectSlot = (doctor, slot) => {
    selectedDoctor.value = doctor
    selectedSlot.value = slot
    checkoutStep.value = 2
}

const bookNow = async () => {
    try {
        await axios.post('/api/patient/book', { slot_id: selectedSlot.value.id })
        checkoutStep.value = 3
        fetchData()
    } catch (err) {
        showMsg(err.response?.data?.msg || 'Booking failed', 'danger')
    }
}

const exportHistory = async () => {
    try {
        await axios.post('/api/patient/export')
        showMsg('CSV Export started! The system is generating your report.')
    } catch (err) {
        showMsg('Failed to trigger export', 'danger')
    }
}

const cancelAppointment = async (id) => {
    if (confirm('Are you sure you want to cancel this appointment?')) {
        try {
            await axios.post(`/api/patient/appointments/${id}/cancel`)
            fetchData()
            showMsg('Appointment cancelled')
        } catch (err) {
            showMsg(err.response?.data?.msg || 'Cancellation failed', 'danger')
        }
    }
}

const viewTreatment = (treatment) => {
    selectedTreatment.value = treatment
}

// --- Reschedule ---
const openReschedule = async (app) => {
    rescheduleApp.value = app
    rescheduleSlot.value = null
    doctors.value = []
    searchQ.value = ''
    selectedSpec.value = ''
    await searchDoctors()
}

const selectRescheduleSlot = (slot) => {
    rescheduleSlot.value = slot
}

const confirmReschedule = async () => {
    if (!rescheduleSlot.value) return showMsg('Please select a new slot', 'danger')
    try {
        await axios.post(`/api/patient/appointments/${rescheduleApp.value.id}/reschedule`, { slot_id: rescheduleSlot.value.id })
        showMsg('Appointment rescheduled successfully')
        fetchData()
        rescheduleApp.value = null
    } catch (err) {
        showMsg(err.response?.data?.msg || 'Reschedule failed', 'danger')
    }
}
</script>

<template>
  <div class="fade-in">
    <!-- Global Status Alert -->
    <div v-if="statusMsg.text" :class="['alert', 'alert-' + statusMsg.type, 'position-fixed', 'top-0', 'end-0', 'm-4', 'shadow-lg']" style="z-index: 9999;">
        {{ statusMsg.text }}
    </div>

    <div class="d-flex justify-content-between align-items-center mb-5">
        <div>
            <h2 class="fw-bold mb-1">My Health Compass</h2>
            <p class="text-muted mb-0">Track your appointments, medical history, and profile</p>
        </div>
        <div class="d-flex gap-2">
            <div class="bg-white p-1 rounded-3 shadow-sm border">
                <div class="btn-group border-0">
                    <button class="btn btn-sm px-3" :class="currentView === 'appointments' ? 'btn-primary shadow-sm' : 'btn-light'" @click="currentView = 'appointments'">Appointments</button>
                    <button class="btn btn-sm px-3" :class="currentView === 'profile' ? 'btn-primary shadow-sm' : 'btn-light'" @click="currentView = 'profile'; fetchProfile()">My Profile</button>
                </div>
            </div>
            <button class="btn btn-outline-primary shadow-sm px-4 fw-bold" @click="exportHistory">
                <i class="bi bi-file-earmark-spreadsheet me-2"></i>Export CSV
            </button>
        </div>
    </div>

    <!-- Appointments View -->
    <div v-if="currentView === 'appointments'" class="row g-4">
      <div class="col-md-12">
        <div class="card border-0 p-4 shadow-sm">
          <div class="d-flex justify-content-between align-items-center mb-4">
            <h4 class="fw-bold mb-0">My Consultations</h4>
            <button class="btn btn-primary shadow-sm px-4 fw-bold" data-bs-toggle="modal" data-bs-target="#bookModal" @click="startBooking">
                <i class="bi bi-plus-lg me-2"></i>New Appointment
            </button>
          </div>
          
          <div v-if="appointments.length === 0" class="text-center py-5">
            <i class="bi bi-calendar2-x text-muted fs-1 d-block mb-3 opacity-25"></i>
            <p class="text-muted">You have no upcoming or past appointments.</p>
          </div>
          
          <div v-else class="table-responsive">
            <table class="table hover align-middle">
                <thead>
                    <tr>
                        <th class="ps-3">Specialist</th>
                        <th>Date & Time</th>
                        <th>Status</th>
                        <th class="text-end pe-3">Actions</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="app in appointments" :key="app.id">
                        <td class="ps-3">
                            <div class="d-flex align-items-center">
                                <div class="bg-primary-subtle text-primary rounded-circle d-flex align-items-center justify-content-center me-3" style="width: 40px; height: 40px;">
                                    <i class="bi bi-person-heart"></i>
                                </div>
                                <div>
                                    <span class="fw-bold d-block">Dr. {{ app.doctor }}</span>
                                    <small class="text-muted">{{ app.specialization }}</small>
                                </div>
                            </div>
                        </td>
                        <td>
                            <span class="d-block fw-semibold">{{ app.date }}</span>
                            <small class="text-muted"><i class="bi bi-clock me-1"></i>{{ app.time }}</small>
                        </td>
                        <td>
                            <span :class="['badge rounded-pill', app.status === 'Completed' ? 'bg-success-subtle text-success' : (app.status === 'Cancelled' ? 'bg-danger-subtle text-danger' : 'bg-primary-subtle text-primary')]">
                                {{ app.status }}
                            </span>
                        </td>
                        <td class="text-end pe-3">
                            <div class="d-flex gap-2 justify-content-end">
                                <button v-if="app.treatment" class="btn btn-sm btn-outline-success shadow-sm px-3 fw-bold" data-bs-toggle="modal" data-bs-target="#treatmentModal" @click="viewTreatment(app.treatment)">
                                    <i class="bi bi-file-earmark-text me-1"></i> View Remarks
                                </button>
                                <button v-if="app.status === 'Booked'" class="btn btn-sm btn-outline-warning border-0" data-bs-toggle="modal" data-bs-target="#rescheduleModal" @click="openReschedule(app)" title="Reschedule">
                                    <i class="bi bi-calendar-check"></i>
                                </button>
                                <button v-if="app.status === 'Booked'" class="btn btn-sm btn-outline-danger border-0" @click="cancelAppointment(app.id)" title="Cancel Appointment">
                                    <i class="bi bi-x-circle"></i>
                                </button>
                            </div>
                        </td>
                    </tr>
                </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- Profile View -->
    <div v-if="currentView === 'profile'" class="row g-4 fade-in">
        <div class="col-md-4">
            <div class="card border-0 p-4 shadow-sm text-center">
                <div class="bg-primary-subtle rounded-circle d-flex align-items-center justify-content-center mx-auto mb-3" style="width: 80px; height: 80px;">
                    <i class="bi bi-person-fill text-primary fs-1"></i>
                </div>
                <h5 class="fw-bold mb-1">{{ profile.name }}</h5>
                <p class="text-muted small mb-2">@{{ profile.username }}</p>
                <span class="badge bg-success-subtle text-success rounded-pill px-3">Active Patient</span>
                <hr>
                <div class="text-start small">
                    <div class="mb-2"><i class="bi bi-envelope me-2 text-muted"></i>{{ profile.email }}</div>
                    <div class="mb-2" v-if="profile.contact"><i class="bi bi-telephone me-2 text-muted"></i>{{ profile.contact }}</div>
                    <div v-if="profile.dob"><i class="bi bi-cake me-2 text-muted"></i>{{ profile.dob }}</div>
                </div>
            </div>
        </div>
        <div class="col-md-8">
            <div class="card border-0 p-4 shadow-sm">
                <h5 class="fw-bold mb-4"><i class="bi bi-pencil-square me-2 text-primary"></i>Edit Profile</h5>
                <form @submit.prevent="saveProfile">
                    <div class="row g-3 mb-3">
                        <div class="col-md-6">
                            <label class="form-label small fw-semibold">Full Name</label>
                            <input v-model="profileForm.name" type="text" class="form-control bg-light border-0" required>
                        </div>
                        <div class="col-md-6">
                            <label class="form-label small fw-semibold">Email</label>
                            <input v-model="profileForm.email" type="email" class="form-control bg-light border-0">
                        </div>
                    </div>
                    <div class="row g-3 mb-3">
                        <div class="col-md-6">
                            <label class="form-label small fw-semibold">Phone / Contact</label>
                            <input v-model="profileForm.contact" type="text" class="form-control bg-light border-0" placeholder="e.g. +91 8888888888">
                        </div>
                        <div class="col-md-6">
                            <label class="form-label small fw-semibold">Date of Birth</label>
                            <input v-model="profileForm.dob" type="date" class="form-control bg-light border-0">
                        </div>
                    </div>
                    <div class="mb-4">
                        <label class="form-label small fw-semibold">New Password <span class="text-muted fw-normal">(leave blank to keep current)</span></label>
                        <input v-model="profileForm.password" type="password" class="form-control bg-light border-0" placeholder="••••••••">
                    </div>
                    <div class="mb-4">
                        <label class="form-label small fw-semibold">Past Treatment Record (PDF/Image)</label>
                        <input type="file" class="form-control bg-light border-0" @change="handleFileUpload" accept=".pdf,.png,.jpg,.jpeg">
                        <small v-if="profile.file" class="text-muted mt-1 d-block">Current file: {{ profile.file }}</small>
                    </div>
                    <button type="submit" class="btn btn-primary px-5 py-2 fw-bold shadow-sm">Save Changes</button>
                </form>
            </div>
        </div>
    </div>

  </div>

  <!-- Booking Modal -->
  <div class="modal fade" id="bookModal" tabindex="-1">
      <div class="modal-dialog modal-dialog-centered modal-xl">
          <div class="modal-content border-0 shadow-lg px-2">
              <div class="modal-header border-0 pb-0">
                  <div>
                      <h4 class="modal-title fw-bold">Appointment Wizard</h4>
                      <div class="d-flex gap-2 mt-2">
                          <span class="small" :class="checkoutStep >= 1 ? 'text-primary' : 'text-muted'"><i class="bi bi-1-circle-fill"></i> Select Slot</span>
                          <span class="text-muted small">/</span>
                          <span class="small" :class="checkoutStep >= 2 ? 'text-primary' : 'text-muted'"><i class="bi bi-2-circle-fill"></i> Payment</span>
                          <span class="text-muted small">/</span>
                          <span class="small" :class="checkoutStep >= 3 ? 'text-primary' : 'text-muted'"><i class="bi bi-3-circle-fill"></i> Finish</span>
                      </div>
                  </div>
                  <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
              </div>
              <div class="modal-body py-4">
                  <!-- Step 1: Search & Select Slot -->
                  <div v-if="checkoutStep === 1" class="fade-in">
                      <div class="row g-3 mb-4">
                          <div class="col-md-7">
                              <div class="input-group rounded-3 shadow-sm overflow-hidden border">
                                  <span class="input-group-text bg-white border-0"><i class="bi bi-search text-muted"></i></span>
                                  <input v-model="searchQ" type="text" class="form-control border-0" placeholder="Doctor name" @input="searchDoctors">
                              </div>
                          </div>
                          <div class="col-md-5">
                              <select v-model="selectedSpec" class="form-select rounded-3 shadow-sm border" @change="searchDoctors">
                                  <option value="">All Specializations</option>
                                  <option v-for="s in specs" :key="s.id" :value="s.id">{{ s.name }}</option>
                              </select>
                          </div>
                      </div>

                      <div class="row g-4 overflow-auto" style="max-height: 50vh;">
                          <div v-for="doc in doctors" :key="doc.id" class="col-md-6">
                              <div class="card h-100 border p-3 bg-light-subtle">
                                  <h6 class="fw-bold mb-1">Dr. {{ doc.name }}</h6>
                                  <p class="text-muted small mb-3">{{ doc.specialization }} • {{ doc.experience }}yrs Exp</p>
                                  <div class="d-flex flex-wrap gap-2">
                                      <button v-for="slot in doc.availability" :key="slot.id" 
                                              class="btn btn-xs btn-white border shadow-sm px-2 py-1 text-primary small fw-bold"
                                              @click="selectSlot(doc, slot)">
                                          <i class="bi bi-clock me-1"></i> {{ slot.date }} • {{ slot.time }}
                                      </button>
                                      <div v-if="doc.availability.length === 0" class="alert alert-light w-100 p-2 border-0 mb-0 small">
                                          <i class="bi bi-info-circle me-1"></i> No slots available
                                      </div>
                                  </div>
                              </div>
                          </div>
                          <div v-if="doctors.length === 0" class="text-center py-5">
                              <p class="text-muted">No doctors found matching your criteria.</p>
                          </div>
                      </div>
                  </div>

                  <!-- Step 2: Dummy Payment -->
                  <div v-if="checkoutStep === 2" class="text-center py-4 fade-in">
                      <div class="mb-4">
                          <h4 class="fw-bold mb-1">Complete Booking</h4>
                          <p class="text-muted">Secure transaction encrypted with 256-bit SSL</p>
                      </div>
                      <div class="card bg-indigo-subtle border-0 p-4 mb-4 mx-auto text-start" style="max-width: 450px; background: #eef2ff;">
                          <div class="d-flex justify-content-between mb-2">
                              <span class="text-muted">Provider:</span>
                              <span class="fw-bold">Dr. {{ selectedDoctor.name }}</span>
                          </div>
                          <div class="d-flex justify-content-between mb-3">
                              <span class="text-muted">Time:</span>
                              <span class="fw-bold">{{ selectedSlot.date }} at {{ selectedSlot.time }}</span>
                          </div>
                          <div class="border-top pt-3 d-flex justify-content-between align-items-center">
                              <span class="h6 mb-0 fw-bold">Consultation Fee</span>
                              <span class="h5 mb-0 fw-bold text-primary">₹500.00</span>
                          </div>
                      </div>
                      <div class="mx-auto text-start" style="max-width: 450px;">
                          <div class="mb-3">
                              <label class="small fw-bold text-muted mb-1">Card Number</label>
                              <input type="text" class="form-control bg-light border-0" placeholder="•••• •••• •••• ••••">
                          </div>
                          <div class="row g-3 mb-4">
                              <div class="col-6">
                                  <label class="small fw-bold text-muted mb-1">Expiry</label>
                                  <input type="text" class="form-control bg-light border-0" placeholder="MM/YY">
                              </div>
                              <div class="col-6">
                                  <label class="small fw-bold text-muted mb-1">CVV</label>
                                  <input type="text" class="form-control bg-light border-0" placeholder="•••">
                              </div>
                          </div>
                          <button class="btn btn-primary w-100 py-3 fw-bold shadow-sm" @click="bookNow">Pay & Confirm Invitation</button>
                      </div>
                  </div>

                  <!-- Step 3: Success -->
                  <div v-if="checkoutStep === 3" class="text-center py-5 fade-in">
                      <div class="bg-success text-white rounded-circle d-inline-flex align-items-center justify-content-center mb-4 shadow-lg" style="width: 80px; height: 80px;">
                          <i class="bi bi-check-lg fs-1"></i>
                      </div>
                      <h3 class="fw-bold">Success! Booking Confirmed</h3>
                      <p class="text-muted mx-auto" style="max-width: 400px;">
                          You'll receive a notification reminder before your appointment starts. 
                          Detailed instructions have been sent to your email.
                      </p>
                      <button class="btn btn-outline-primary mt-4 px-4 fw-bold" data-bs-dismiss="modal">Back to Dashboard</button>
                  </div>
              </div>
          </div>
      </div>
  </div>

  <!-- Reschedule Modal -->
  <div class="modal fade" id="rescheduleModal" tabindex="-1">
      <div class="modal-dialog modal-dialog-centered modal-xl">
          <div class="modal-content border-0 shadow-lg px-2">
              <div class="modal-header border-0 pb-0">
                  <div>
                      <h4 class="modal-title fw-bold"><i class="bi bi-calendar-check me-2 text-warning"></i>Reschedule Appointment</h4>
                      <p class="text-muted small mt-1 mb-0">Current: Dr. {{ rescheduleApp?.doctor }} on {{ rescheduleApp?.date }} at {{ rescheduleApp?.time }}</p>
                  </div>
                  <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
              </div>
              <div class="modal-body py-4">
                  <!-- Search filters -->
                  <div class="row g-3 mb-4">
                      <div class="col-md-7">
                          <div class="input-group rounded-3 shadow-sm overflow-hidden border">
                              <span class="input-group-text bg-white border-0"><i class="bi bi-search text-muted"></i></span>
                              <input v-model="searchQ" type="text" class="form-control border-0" placeholder="Doctor name" @input="searchDoctors">
                          </div>
                      </div>
                      <div class="col-md-5">
                          <select v-model="selectedSpec" class="form-select rounded-3 shadow-sm border" @change="searchDoctors">
                              <option value="">All Specializations</option>
                              <option v-for="s in specs" :key="s.id" :value="s.id">{{ s.name }}</option>
                          </select>
                      </div>
                  </div>

                  <!-- Selected new slot indicator -->
                  <div v-if="rescheduleSlot" class="alert alert-primary border-0 shadow-sm mb-4">
                      <i class="bi bi-check-circle-fill me-2"></i>
                      New slot selected: <strong>{{ rescheduleSlot.date }} at {{ rescheduleSlot.time }}</strong>
                  </div>

                  <!-- Doctor / Slot grid -->
                  <div class="row g-4 overflow-auto" style="max-height: 42vh;">
                      <div v-for="doc in doctors" :key="doc.id" class="col-md-6">
                          <div class="card h-100 border p-3 bg-light-subtle">
                              <h6 class="fw-bold mb-1">Dr. {{ doc.name }}</h6>
                              <p class="text-muted small mb-3">{{ doc.specialization }} • {{ doc.experience }}yrs Exp</p>
                              <div class="d-flex flex-wrap gap-2">
                                  <button v-for="slot in doc.availability" :key="slot.id"
                                          :class="['btn btn-xs border shadow-sm px-2 py-1 small fw-bold', rescheduleSlot?.id === slot.id ? 'btn-warning text-dark' : 'btn-white text-primary']"
                                          @click="selectRescheduleSlot(slot)">
                                      <i class="bi bi-clock me-1"></i> {{ slot.date }} • {{ slot.time }}
                                  </button>
                                  <div v-if="doc.availability.length === 0" class="alert alert-light w-100 p-2 border-0 mb-0 small">
                                      <i class="bi bi-info-circle me-1"></i> No slots available
                                  </div>
                              </div>
                          </div>
                      </div>
                      <div v-if="doctors.length === 0" class="text-center py-5">
                          <p class="text-muted">No doctors found matching your criteria.</p>
                      </div>
                  </div>
              </div>
              <div class="modal-footer border-0">
                  <button type="button" class="btn btn-light px-4" data-bs-dismiss="modal">Cancel</button>
                  <button type="button" class="btn btn-warning fw-bold px-4 shadow-sm" :disabled="!rescheduleSlot" @click="confirmReschedule" data-bs-dismiss="modal">
                      <i class="bi bi-calendar-check me-2"></i>Confirm Reschedule
                  </button>
              </div>
          </div>
      </div>
  </div>

  <!-- Treatment Modal -->
  <div class="modal fade" id="treatmentModal" tabindex="-1">
      <div class="modal-dialog modal-dialog-centered">
          <div class="modal-content border-0 shadow-lg overflow-hidden">
              <div class="bg-success p-3 text-white text-center">
                  <i class="bi bi-journal-check fs-2"></i>
                  <h5 class="modal-title fw-bold mt-1">Consultation Outcome</h5>
              </div>
              <div class="modal-body p-4" v-if="selectedTreatment">
                  <div class="mb-4">
                      <label class="small text-uppercase fw-bold text-muted mb-1">Diagnosis</label>
                      <h5 class="fw-bold text-dark">{{ selectedTreatment.diagnosis }}</h5>
                  </div>
                  <div class="mb-4">
                      <label class="small text-uppercase fw-bold text-muted mb-1">Prescription</label>
                      <div class="bg-light p-3 rounded-3 font-monospace small">
                          {{ selectedTreatment.prescription }}
                      </div>
                  </div>
                  <div v-if="selectedTreatment.notes" class="p-3 bg-light-subtle rounded-3 border-start border-4 border-success">
                      <label class="small text-uppercase fw-bold text-muted mb-1 d-block">Doctor's Notes</label>
                      <p class="mb-0 small italic">{{ selectedTreatment.notes }}</p>
                  </div>
              </div>
              <div class="modal-footer border-0">
                  <button type="button" class="btn btn-light w-100" data-bs-dismiss="modal">Close</button>
              </div>
          </div>
      </div>
  </div>
</template>
