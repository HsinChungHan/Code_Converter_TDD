# Test Scenarios

## 測試分類

| 類別 | 範圍 | 工具 |
|------|------|------|
| Unit Test | UseCase, Repository, Domain Model | XCTest |
| Integration Test | Feature (TCA), API Client | XCTest + TCA TestStore |
| UI Test | View 交互 | XCUITest |

---

## Unit Tests

### 1. WidgetInputState Tests

```swift
class WidgetInputStateTests: XCTestCase {
    
    func test_default_state_properties() {
        let state = WidgetInputState.default
        
        XCTAssertFalse(state.showFocusBorder)
        XCTAssertFalse(state.showErrorBorder)
        XCTAssertFalse(state.showClearButton)
        XCTAssertFalse(state.isLoadButtonEnabled)
    }
    
    func test_focus_state_shows_border() {
        let state = WidgetInputState.focus
        
        XCTAssertTrue(state.showFocusBorder)
        XCTAssertFalse(state.showErrorBorder)
    }
    
    func test_typing_state_enables_load_button() {
        let state = WidgetInputState.typing
        
        XCTAssertTrue(state.showFocusBorder)
        XCTAssertTrue(state.showClearButton)
        XCTAssertTrue(state.isLoadButtonEnabled)
    }
    
    func test_error_state_shows_red_border() {
        let state = WidgetInputState.error(message: "Error message")
        
        XCTAssertFalse(state.showFocusBorder)
        XCTAssertTrue(state.showErrorBorder)
        XCTAssertTrue(state.showClearButton)
        XCTAssertEqual(state.errorMessage, "Error message")
    }
    
    func test_loading_state_disables_interactions() {
        let state = WidgetInputState.loading
        
        XCTAssertFalse(state.showClearButton)
        XCTAssertFalse(state.isLoadButtonEnabled)
    }
}
```

### 2. SelectedBookie Tests

```swift
class SelectedBookieTests: XCTestCase {
    
    func test_displayText_format() {
        let bookie = SelectedBookie(provider: "bet9ja", name: "Bet9ja", country: .nigeria)
        
        XCTAssertEqual(bookie.displayText, "Bet9ja NG")
    }
    
    func test_shortDisplayText_truncates_long_name() {
        let bookie = SelectedBookie(provider: "longbookie", name: "Very Long Bookie Name", country: .nigeria)
        
        XCTAssertEqual(bookie.shortDisplayText, "Very Long Bo… NG")
    }
    
    func test_init_from_providerConfig_uses_first_country() {
        let config = ProviderConfig(
            id: "betway",
            provider: "betway",
            name: "Betway",
            countries: [.ghana, .nigeria, .kenya]
        )
        
        let bookie = SelectedBookie(from: config)
        
        XCTAssertEqual(bookie?.country, .ghana)
    }
    
    func test_init_from_empty_providerConfig_returns_nil() {
        let config = ProviderConfig(
            id: "empty",
            provider: "empty",
            name: "Empty",
            countries: []
        )
        
        XCTAssertNil(SelectedBookie(from: config))
    }
}
```

### 3. ConvertResult Tests

```swift
class ConvertResultTests: XCTestCase {
    
    func test_failCnt_counts_failed_selections() {
        let result = ConvertResult(
            shareCode: "ABC123",
            selections: [
                .mock(isFailed: false),
                .mock(isFailed: true),
                .mock(isFailed: true),
                .mock(isFailed: false)
            ]
        )
        
        XCTAssertEqual(result.failCnt, 2)
        XCTAssertEqual(result.successCnt, 2)
    }
    
    func test_hasPartialFailure_when_some_failed() {
        let result = ConvertResult(
            shareCode: "ABC123",
            selections: [
                .mock(isFailed: false),
                .mock(isFailed: true)
            ]
        )
        
        XCTAssertTrue(result.hasPartialFailure)
        XCTAssertFalse(result.isAllFailed)
    }
    
    func test_isAllFailed_when_all_failed() {
        let result = ConvertResult(
            shareCode: "ABC123",
            selections: [
                .mock(isFailed: true),
                .mock(isFailed: true)
            ]
        )
        
        XCTAssertTrue(result.isAllFailed)
        XCTAssertFalse(result.hasPartialFailure)
    }
}
```

---

## TCA Feature Tests

### 1. Happy Path: Load Provider Config

```swift
@MainActor
class LoadCodeWidgetFeatureTests: XCTestCase {
    
    func test_bookieDropdownTapped_loads_config_and_shows_sheet() async {
        let mockConfigs = [
            ProviderConfig(id: "bet9ja", provider: "bet9ja", name: "Bet9ja", countries: [.nigeria])
        ]
        
        let store = TestStore(initialState: LoadCodeWidget.State(enableCodeConverter: true)) {
            LoadCodeWidget.Feature()
        } withDependencies: {
            $0.loadProviderConfigUseCase = .init { .success(mockConfigs) }
        }
        
        await store.send(.bookieDropdownTapped)
        
        await store.receive(.providerConfigLoaded(.success(mockConfigs))) {
            $0.providerConfigs = mockConfigs
            $0.isBookieSelectorPresented = true
            $0.availableCountries = [.nigeria]
        }
    }
}
```

### 2. Happy Path: Convert Booking Code

```swift
func test_loadBookingCode_with_codeConverter_converts_and_presents_betslip() async {
    let mockOutput = ConvertBookingCodeOutput(
        convertResult: ConvertResult(shareCode: "FCOM123", selections: [.mock(isFailed: false)]),
        liabilities: .mock
    )
    
    let store = TestStore(initialState: LoadCodeWidget.State(
        bookingCode: "3RA3FA",
        enableCodeConverter: true,
        selectedBookie: SelectedBookie(provider: "bet9ja", name: "Bet9ja", country: .nigeria)
    )) {
        LoadCodeWidget.Feature()
    } withDependencies: {
        $0.convertBookingCodeUseCase = .init { _ in .success(mockOutput) }
    }
    
    await store.send(.loadBookingCode) {
        $0.inputState = .loading
        $0.isLoading = true
    }
    
    await store.receive(.convertCodeCompleted(.success(mockOutput))) {
        $0.isLoading = false
        $0.inputState = .filled
        $0.bookingCode = ""
        $0.convertResult = mockOutput.convertResult
    }
    
    await store.receive(.presentBetslip(shareCode: "FCOM123", failCnt: 0))
}
```

### 3. Error: Code Not Found

```swift
func test_loadBookingCode_codeNotFound_shows_error() async {
    let store = TestStore(initialState: LoadCodeWidget.State(
        bookingCode: "INVALID",
        enableCodeConverter: true,
        selectedBookie: SelectedBookie(provider: "bet9ja", name: "Bet9ja", country: .nigeria)
    )) {
        LoadCodeWidget.Feature()
    } withDependencies: {
        $0.convertBookingCodeUseCase = .init { _ in
            .failure(CodeConverterError.codeNotFound(bookieName: "Bet9ja"))
        }
    }
    
    await store.send(.loadBookingCode) {
        $0.inputState = .loading
        $0.isLoading = true
    }
    
    await store.receive(.convertCodeCompleted(.failure(CodeConverterError.codeNotFound(bookieName: "Bet9ja")))) {
        $0.isLoading = false
        $0.inputState = .error(message: "We couldn't find this booking code on Bet9ja. Please check and try again.")
        $0.errorMessage = "We couldn't find this booking code on Bet9ja. Please check and try again."
    }
}
```

### 4. Input State Transitions

```swift
func test_inputState_transitions() async {
    let store = TestStore(initialState: LoadCodeWidget.State(enableCodeConverter: true)) {
        LoadCodeWidget.Feature()
    }
    
    // Default → Focus
    await store.send(.inputFocused) {
        $0.inputState = .focus
    }
    
    // Focus → Typing (when text entered)
    await store.send(.bookingCodeChanged("3RA")) {
        $0.bookingCode = "3RA"
        $0.inputState = .typing
    }
    
    // Typing → Focus (when cleared)
    await store.send(.clearButtonTapped) {
        $0.bookingCode = ""
        $0.inputState = .focus
        $0.errorMessage = nil
    }
    
    // Focus → Default (when blurred with no text)
    await store.send(.inputBlurred) {
        $0.inputState = .default
    }
}
```

### 5. Bookie Selection

```swift
func test_bookieSelected_updates_state_and_closes_sheet() async {
    let configs = [
        ProviderConfig(id: "betway", provider: "betway", name: "Betway", countries: [.ghana, .nigeria])
    ]
    
    let store = TestStore(initialState: LoadCodeWidget.State(
        enableCodeConverter: true,
        providerConfigs: configs,
        isBookieSelectorPresented: true
    )) {
        LoadCodeWidget.Feature()
    }
    
    await store.send(.bookieSelected(provider: "betway", country: .ghana)) {
        $0.selectedBookie = SelectedBookie(provider: "betway", name: "Betway", country: .ghana)
        $0.selectedCountry = .ghana  // 向後相容
        $0.isBookieSelectorPresented = false
    }
}
```

---

## UI Tests

### 1. Input Field Focus

```swift
func test_input_field_shows_green_border_when_focused() {
    let app = XCUIApplication()
    app.launch()
    
    let inputField = app.textFields["bookingCodeInput"]
    inputField.tap()
    
    // 驗證綠色邊框存在（透過 accessibility identifier）
    XCTAssertTrue(inputField.otherElements["focusBorder"].exists)
}
```

### 2. Clear Button

```swift
func test_clear_button_clears_input() {
    let app = XCUIApplication()
    app.launch()
    
    let inputField = app.textFields["bookingCodeInput"]
    inputField.tap()
    inputField.typeText("3RA3FA")
    
    let clearButton = app.buttons["clearButton"]
    XCTAssertTrue(clearButton.exists)
    
    clearButton.tap()
    
    XCTAssertEqual(inputField.value as? String, "")
}
```

### 3. Bookie Selector Sheet

```swift
func test_dropdown_opens_bookie_selector_sheet() {
    let app = XCUIApplication()
    app.launch()
    
    let dropdown = app.buttons["bookieDropdown"]
    dropdown.tap()
    
    // 驗證 Sheet 出現
    XCTAssertTrue(app.sheets["bookieSelectorSheet"].waitForExistence(timeout: 2))
    
    // 選擇 Bookie
    app.buttons["Bet9ja"].tap()
    
    // 驗證 Sheet 關閉
    XCTAssertFalse(app.sheets["bookieSelectorSheet"].exists)
    
    // 驗證 Dropdown 文字更新
    XCTAssertTrue(dropdown.label.contains("Bet9ja"))
}
```

---

## Test Data Mocks

```swift
extension ConvertResult.Selection {
    static func mock(
        eventId: String = "12345",
        sportId: Int = 1,
        isFailed: Bool = false,
        failReason: String? = nil
    ) -> Self {
        Self(
            eventId: eventId,
            sportId: sportId,
            marketId: 10,
            selectionId: 100,
            odds: 1.85,
            specialBetValue: nil,
            isFailed: isFailed,
            failReason: failReason
        )
    }
}

extension LiabilitiesResult {
    static var mock: Self {
        Self(isValid: true, liabilities: [])
    }
}
```
