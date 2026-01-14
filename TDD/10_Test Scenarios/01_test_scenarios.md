# Test Scenarios

## ⚠️ BE 新設計更新 (2025-01-14)

| 變更項目 | 說明 |
|----------|------|
| **移除 Bookie 相關測試** | `SelectedBookie`, `bookieDropdownTapped`, `bookieSelected` 測試已移除 |
| **移除 Config 相關測試** | `LoadProviderConfig` 測試已移除 |
| **新增 Tooltip 測試** | 新增 Tooltip 顯示邏輯測試 |

---

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

### 2. ConvertResult Tests

```swift
class ConvertResultTests: XCTestCase {
    
    func test_hasPartialFailure_when_some_failed() {
        let result = ConvertResult(
            shareCode: "ABC123",
            successCnt: 5,
            failCnt: 2
        )
        
        XCTAssertTrue(result.hasPartialFailure)
        XCTAssertFalse(result.isAllFailed)
    }
    
    func test_isAllFailed_when_all_failed() {
        let result = ConvertResult(
            shareCode: "ABC123",
            successCnt: 0,
            failCnt: 5
        )
        
        XCTAssertTrue(result.isAllFailed)
        XCTAssertFalse(result.hasPartialFailure)
    }
    
    func test_success_when_no_failures() {
        let result = ConvertResult(
            shareCode: "ABC123",
            successCnt: 5,
            failCnt: 0
        )
        
        XCTAssertFalse(result.hasPartialFailure)
        XCTAssertFalse(result.isAllFailed)
    }
}
```

### 3. TooltipStorage Tests

```swift
class TooltipStorageTests: XCTestCase {
    
    var userDefaults: UserDefaults!
    var storage: TooltipStorage!
    
    override func setUp() {
        super.setUp()
        userDefaults = UserDefaults(suiteName: "test")
        userDefaults.removePersistentDomain(forName: "test")
        storage = TooltipStorage(userDefaults: userDefaults)
    }
    
    func test_shouldShowTooltip_returns_true_initially() {
        XCTAssertTrue(storage.shouldShowTooltip)
    }
    
    func test_dismissTooltip_sets_flag() {
        storage.dismissTooltip()
        
        XCTAssertFalse(storage.shouldShowTooltip)
    }
    
    func test_shouldShowTooltip_persists_after_dismiss() {
        storage.dismissTooltip()
        
        // 重新創建 storage 模擬 app 重啟
        let newStorage = TooltipStorage(userDefaults: userDefaults)
        
        XCTAssertFalse(newStorage.shouldShowTooltip)
    }
}
```

---

## TCA Feature Tests

### 1. Happy Path: Convert Booking Code

```swift
@MainActor
class LoadCodeWidgetFeatureTests: XCTestCase {
    
    func test_loadBookingCode_converts_and_presents_betslip() async {
        let mockOutput = ConvertBookingCodeOutput(
            convertResult: ConvertResult(shareCode: "FCOM123", successCnt: 5, failCnt: 0),
            liabilities: .mock
        )
        
        let store = TestStore(initialState: LoadCodeWidget.State(
            bookingCode: "3RA3FA",
            enableCodeConverter: true
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
}
```

### 2. Partial Success: Shows Toast

```swift
func test_loadBookingCode_partial_success_shows_toast() async {
    let mockOutput = ConvertBookingCodeOutput(
        convertResult: ConvertResult(shareCode: "FCOM123", successCnt: 3, failCnt: 2),
        liabilities: .mock
    )
    
    let store = TestStore(initialState: LoadCodeWidget.State(
        bookingCode: "3RA3FA",
        enableCodeConverter: true
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
    
    // failCnt > 0，應顯示 Toast
    await store.receive(.presentBetslip(shareCode: "FCOM123", failCnt: 2))
}
```

### 3. Error: Code Not Found

```swift
func test_loadBookingCode_codeNotFound_shows_error() async {
    let store = TestStore(initialState: LoadCodeWidget.State(
        bookingCode: "INVALID",
        enableCodeConverter: true
    )) {
        LoadCodeWidget.Feature()
    } withDependencies: {
        $0.convertBookingCodeUseCase = .init { _ in
            .failure(CodeConverterError.codeNotFound)
        }
    }
    
    await store.send(.loadBookingCode) {
        $0.inputState = .loading
        $0.isLoading = true
    }
    
    await store.receive(.convertCodeCompleted(.failure(CodeConverterError.codeNotFound))) {
        $0.isLoading = false
        $0.inputState = .error(message: "We couldn't find this booking code. Please check and try again.")
        $0.errorMessage = "We couldn't find this booking code. Please check and try again."
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

### 5. Tooltip Tests

```swift
func test_onAppear_shows_tooltip_if_not_dismissed() async {
    let store = TestStore(initialState: LoadCodeWidget.State(enableCodeConverter: true)) {
        LoadCodeWidget.Feature()
    } withDependencies: {
        $0.tooltipStorage = TooltipStorage(shouldShowTooltip: true)
    }
    
    await store.send(.onAppear) {
        $0.isTooltipVisible = true
    }
}

func test_onAppear_hides_tooltip_if_dismissed() async {
    let store = TestStore(initialState: LoadCodeWidget.State(enableCodeConverter: true)) {
        LoadCodeWidget.Feature()
    } withDependencies: {
        $0.tooltipStorage = TooltipStorage(shouldShowTooltip: false)
    }
    
    await store.send(.onAppear) {
        $0.isTooltipVisible = false
    }
}

func test_tooltipDismissed_hides_tooltip_and_persists() async {
    var dismissCalled = false
    
    let store = TestStore(initialState: LoadCodeWidget.State(
        enableCodeConverter: true,
        isTooltipVisible: true
    )) {
        LoadCodeWidget.Feature()
    } withDependencies: {
        $0.tooltipStorage = TooltipStorage(
            shouldShowTooltip: true,
            onDismiss: { dismissCalled = true }
        )
    }
    
    await store.send(.tooltipDismissed) {
        $0.isTooltipVisible = false
    }
    
    XCTAssertTrue(dismissCalled)
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

### 3. Tooltip

```swift
func test_tooltip_shows_on_first_launch() {
    let app = XCUIApplication()
    app.launchArguments.append("--reset-tooltip")
    app.launch()
    
    let tooltip = app.staticTexts["Insert a booking code from any provider"]
    XCTAssertTrue(tooltip.waitForExistence(timeout: 2))
    
    // 點擊關閉
    app.buttons["tooltipCloseButton"].tap()
    
    XCTAssertFalse(tooltip.exists)
}

func test_tooltip_does_not_show_after_dismissed() {
    let app = XCUIApplication()
    // 不重置 tooltip
    app.launch()
    
    let tooltip = app.staticTexts["Insert a booking code from any provider"]
    XCTAssertFalse(tooltip.exists)
}
```

---

## Test Data Mocks

```swift
extension ConvertResult {
    static func mock(
        shareCode: String = "ABC123",
        successCnt: Int = 5,
        failCnt: Int = 0
    ) -> Self {
        Self(
            shareCode: shareCode,
            successCnt: successCnt,
            failCnt: failCnt
        )
    }
}

extension LiabilitiesResult {
    static var mock: Self {
        Self(isValid: true, liabilities: [])
    }
}

extension TooltipStorage {
    init(shouldShowTooltip: Bool, onDismiss: @escaping () -> Void = {}) {
        self._shouldShowTooltip = shouldShowTooltip
        self._onDismiss = onDismiss
    }
}
```

---

## 廢棄的測試

| 測試 | 原因 |
|------|------|
| `SelectedBookieTests` | `SelectedBookie` 已廢棄 |
| `test_bookieDropdownTapped_loads_config` | Bookie Dropdown 已移除 |
| `test_bookieSelected_updates_state` | Bookie 選擇已移除 |
| `LoadProviderConfigUseCaseTests` | Config API 已廢棄 |
