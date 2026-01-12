import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { setupServer } from 'msw/node'
import { HttpResponse, http } from 'msw'
import { useBook } from '@/hooks/useBook'
import { agentApiService } from '@/services/agentApi'

// Mock booking component for testing
type BookingComponentProps = {
  onBook: (params: any) => Promise<void>
  loading: boolean
  error: any
  results: any
}

const BookingComponent = ({ onBook, loading, error, results }: BookingComponentProps) => {
  return (
    <div>
      <h2>Book Travel</h2>
      <div>
        <label>Customer Name:</label>
        <input data-testid="customer-name-input" defaultValue="John Doe" />
      </div>
      <div>
        <label>Email:</label>
        <input data-testid="email-input" defaultValue="john.doe@example.com" />
      </div>
      <div>
        <label>Phone:</label>
        <input data-testid="phone-input" defaultValue="+1-555-0123" />
      </div>
      <div>
        <label>Destination:</label>
        <input data-testid="destination-input" defaultValue="Tokyo" />
      </div>
      <div>
        <label>Departure Date:</label>
        <input data-testid="departure-date-input" defaultValue="2025-02-01" />
      </div>
      <div>
        <label>Return Date:</label>
        <input data-testid="return-date-input" defaultValue="2025-02-14" />
      </div>
      <div>
        <label>Travelers:</label>
        <input data-testid="travelers-input" defaultValue="2" />
      </div>
      <button data-testid="book-button" onClick={() => {
        const customerName = (document.querySelector('[data-testid="customer-name-input"]') as HTMLInputElement).value
        const email = (document.querySelector('[data-testid="email-input"]') as HTMLInputElement).value
        const phone = (document.querySelector('[data-testid="phone-input"]') as HTMLInputElement).value
        const destination = (document.querySelector('[data-testid="destination-input"]') as HTMLInputElement).value
        const departureDate = (document.querySelector('[data-testid="departure-date-input"]') as HTMLInputElement).value
        const returnDate = (document.querySelector('[data-testid="return-date-input"]') as HTMLInputElement).value
        const travelers = parseInt((document.querySelector('[data-testid="travelers-input"]') as HTMLInputElement).value)
        
        onBook({
          customer_info: { name: customerName, email, phone },
          trip_details: { destination, departure_date: departureDate, return_date: returnDate, travelers },
          selected_flight: { flight_id: 'FL123', airline: 'Sample Airline', flight_number: 'SA123', total_price: 1200.0 },
          selected_hotel: { hotel_id: 'HT456', name: 'Sample Hotel', total_price: 840.0 },
          passengers: [
            { first_name: 'John', last_name: 'Doe', email: 'john.doe@example.com' },
            { first_name: 'Jane', last_name: 'Doe', email: 'jane.doe@example.com' }
          ]
        })
      }} disabled={loading}>
        {loading ? 'Booking...' : 'Book Now'}
      </button>
      
      {error && <div data-testid="error-message" className="error">{error.message}</div>}
      
      {results && (
        <div data-testid="booking-results">
          <h3>Booking Confirmation</h3>
          <p>Booking ID: {results.booking_id}</p>
          <p>Status: {results.status}</p>
          <p>Total: ${results.price_breakdown?.total}</p>
        </div>
      )}
    </div>
  )
}

// Create mock server
const server = setupServer()

// Mock data
const mockBookResponse = {
  success: true,
  task_id: 'test-booking-task-id-789',
  booking_id: 'BOOK-123456789',
  status: 'confirmed',
  confirmation_number: 'CONF-987654321',
  price_breakdown: {
    flights_total: 1200.0,
    hotels_total: 840.0,
    services_total: 50.0,
    subtotal: 2090.0,
    taxes_and_fees: 150.0,
    total: 2240.0
  },
  trip_summary: {
    destination: 'Tokyo',
    departure_date: '2025-02-01',
    return_date: '2025-02-14',
    travelers: 2
  },
  next_steps: [
    'Check your email for confirmation',
    'Download your itinerary',
    'Contact customer support if needed'
  ]
}

describe('Booking Integration Tests', () => {
  beforeEach(() => {
    // Start mock server before each test
    server.listen()
  })

  afterEach(() => {
    // Reset and close mock server after each test
    server.resetHandlers()
    server.close()
  })

  it('should render booking component and handle user input', async () => {
    const mockOnBook = vi.fn()
    
    render(
      <BookingComponent 
        onBook={mockOnBook}
        loading={false}
        error={null}
        results={null}
      />
    )

    // Verify component renders correctly
    expect(screen.getByText('Book Travel')).toBeInTheDocument()
    expect(screen.getByTestId('customer-name-input')).toHaveValue('John Doe')
    expect(screen.getByTestId('book-button')).toBeInTheDocument()
  })

  it('should handle book button click and call onBook', async () => {
    const mockOnBook = vi.fn()
    
    render(
      <BookingComponent 
        onBook={mockOnBook}
        loading={false}
        error={null}
        results={null}
      />
    )

    const bookButton = screen.getByTestId('book-button')
    await userEvent.click(bookButton)

    expect(mockOnBook).toHaveBeenCalled()
    const callArgs = mockOnBook.mock.calls[0][0]
    expect(callArgs.customer_info.name).toBe('John Doe')
    expect(callArgs.trip_details.destination).toBe('Tokyo')
    expect(callArgs.passengers.length).toBe(2)
  })

  it('should show loading state during booking', async () => {
    const mockOnBook = vi.fn().mockImplementation(() => new Promise(resolve => setTimeout(resolve, 100)))
    
    const { rerender } = render(
      <BookingComponent 
        onBook={mockOnBook}
        loading={false}
        error={null}
        results={null}
      />
    )

    const bookButton = screen.getByTestId('book-button')
    await userEvent.click(bookButton)

    // Update to loading state
    rerender(
      <BookingComponent 
        onBook={mockOnBook}
        loading={true}
        error={null}
        results={null}
      />
    )

    expect(screen.getByTestId('book-button')).toHaveTextContent('Booking...')
    expect(screen.getByTestId('book-button')).toBeDisabled()
  })

  it('should display booking confirmation after successful booking', async () => {
    const mockOnBook = vi.fn().mockResolvedValue(mockBookResponse)
    
    const { rerender } = render(
      <BookingComponent 
        onBook={mockOnBook}
        loading={false}
        error={null}
        results={null}
      />
    )

    const bookButton = screen.getByTestId('book-button')
    await userEvent.click(bookButton)

    // Update to show results
    rerender(
      <BookingComponent 
        onBook={mockOnBook}
        loading={false}
        error={null}
        results={mockBookResponse}
      />
    )

    expect(screen.getByTestId('booking-results')).toBeInTheDocument()
    expect(screen.getByText('Booking Confirmation')).toBeInTheDocument()
    expect(screen.getByText('Booking ID: BOOK-123456789')).toBeInTheDocument()
    expect(screen.getByText('Status: confirmed')).toBeInTheDocument()
    expect(screen.getByText('Total: $2240')).toBeInTheDocument()
  })

  it('should display error message when booking fails', async () => {
    const mockError = new Error('Booking failed')
    const mockOnBook = vi.fn().mockRejectedValue(mockError)
    
    const { rerender } = render(
      <BookingComponent 
        onBook={mockOnBook}
        loading={false}
        error={null}
        results={null}
      />
    )

    const bookButton = screen.getByTestId('book-button')
    await userEvent.click(bookButton)

    // Update to show error
    rerender(
      <BookingComponent 
        onBook={mockOnBook}
        loading={false}
        error={mockError}
        results={null}
      />
    )

    expect(screen.getByTestId('error-message')).toBeInTheDocument()
    expect(screen.getByText('Booking failed')).toBeInTheDocument()
  })

  it('should handle API mocking with MSW', async () => {
    // Setup mock handler
    server.use(
      http.post('http://localhost:8000/api/agent/book', () => {
        return HttpResponse.json(mockBookResponse)
      })
    )

    // Mock the agentApiService.book method
    const originalBook = agentApiService.book
    agentApiService.book = vi.fn().mockImplementation(async (params) => {
      const response = await fetch('http://localhost:8000/api/agent/book', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(params)
      })
      return response.json()
    })

    const { book } = useBook()
    
    // Test the book function
    const bookParams = {
      customer_info: {
        name: 'John Doe',
        email: 'john.doe@example.com',
        phone: '+1-555-0123'
      },
      trip_details: {
        destination: 'Tokyo',
        departure_date: '2025-02-01',
        return_date: '2025-02-14',
        travelers: 2
      },
      selected_flight: {
        flight_id: 'FL123',
        airline: 'Sample Airline',
        flight_number: 'SA123',
        total_price: 1200.0
      },
      selected_hotel: {
        hotel_id: 'HT456',
        name: 'Sample Hotel',
        total_price: 840.0
      },
      passengers: [
        {
          first_name: 'John',
          last_name: 'Doe',
          email: 'john.doe@example.com'
        },
        {
          first_name: 'Jane',
          last_name: 'Doe',
          email: 'jane.doe@example.com'
        }
      ]
    }

    const result = await book(bookParams)
    
    expect(result).toEqual(mockBookResponse)
    expect(agentApiService.book).toHaveBeenCalledWith(bookParams)

    // Restore original method
    agentApiService.book = originalBook
  })

  it('should handle user input changes for booking details', async () => {
    const mockOnBook = vi.fn()
    
    render(
      <BookingComponent 
        onBook={mockOnBook}
        loading={false}
        error={null}
        results={null}
      />
    )

    const customerNameInput = screen.getByTestId('customer-name-input')
    const emailInput = screen.getByTestId('email-input')
    const travelersInput = screen.getByTestId('travelers-input')

    // Change input values
    await userEvent.clear(customerNameInput)
    await userEvent.type(customerNameInput, 'Jane Smith')
    await userEvent.clear(emailInput)
    await userEvent.type(emailInput, 'jane.smith@example.com')
    await userEvent.clear(travelersInput)
    await userEvent.type(travelersInput, '3')

    const bookButton = screen.getByTestId('book-button')
    await userEvent.click(bookButton)

    const callArgs = mockOnBook.mock.calls[0][0]
    expect(callArgs.customer_info.name).toBe('Jane Smith')
    expect(callArgs.customer_info.email).toBe('jane.smith@example.com')
    expect(callArgs.trip_details.travelers).toBe(3)
  })
})