Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

$ErrorActionPreference = "Stop"
$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")

function Add-SourcePath {
    param(
        [System.Windows.Forms.ListBox]$ListBox,
        [string]$Path
    )
    if (-not $Path -or -not (Test-Path -LiteralPath $Path)) {
        return
    }
    $resolved = (Resolve-Path -LiteralPath $Path).Path
    for ($i = 0; $i -lt $ListBox.Items.Count; $i++) {
        if ($ListBox.Items[$i] -eq $resolved) {
            return
        }
    }
    $ListBox.Items.Add($resolved) | Out-Null
}

function Append-Log {
    param(
        [System.Windows.Forms.TextBox]$TextBox,
        [string]$Message
    )
    $TextBox.AppendText("[$(Get-Date -Format 'HH:mm:ss')] $Message`r`n")
    $TextBox.SelectionStart = $TextBox.TextLength
    $TextBox.ScrollToCaret()
    [System.Windows.Forms.Application]::DoEvents()
}

function Invoke-LoggedProcess {
    param(
        [string]$FilePath,
        [string[]]$Arguments,
        [string]$WorkingDirectory,
        [System.Windows.Forms.TextBox]$LogBox
    )

    Append-Log $LogBox ("RUN: {0} {1}" -f $FilePath, ($Arguments -join " "))

    $psi = [System.Diagnostics.ProcessStartInfo]::new()
    $psi.FileName = $FilePath
    foreach ($arg in $Arguments) {
        $psi.ArgumentList.Add($arg)
    }
    $psi.WorkingDirectory = $WorkingDirectory
    $psi.UseShellExecute = $false
    $psi.CreateNoWindow = $true
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true

    $proc = [System.Diagnostics.Process]::Start($psi)
    while (-not $proc.HasExited) {
        while (-not $proc.StandardOutput.EndOfStream) {
            Append-Log $LogBox $proc.StandardOutput.ReadLine()
        }
        while (-not $proc.StandardError.EndOfStream) {
            Append-Log $LogBox $proc.StandardError.ReadLine()
        }
        Start-Sleep -Milliseconds 100
        [System.Windows.Forms.Application]::DoEvents()
    }

    while (-not $proc.StandardOutput.EndOfStream) {
        Append-Log $LogBox $proc.StandardOutput.ReadLine()
    }
    while (-not $proc.StandardError.EndOfStream) {
        Append-Log $LogBox $proc.StandardError.ReadLine()
    }

    if ($proc.ExitCode -ne 0) {
        throw "Command failed with exit code $($proc.ExitCode): $FilePath"
    }
}

$font = [System.Drawing.Font]::new("Segoe UI", 9)
$titleFont = [System.Drawing.Font]::new("Segoe UI", 14, [System.Drawing.FontStyle]::Bold)

$form = [System.Windows.Forms.Form]::new()
$form.Text = "Academic-RAG PDF Importer"
$form.Size = [System.Drawing.Size]::new(920, 680)
$form.MinimumSize = [System.Drawing.Size]::new(820, 580)
$form.StartPosition = "CenterScreen"
$form.Font = $font

$title = [System.Windows.Forms.Label]::new()
$title.Text = "Academic-RAG PDF Importer"
$title.Font = $titleFont
$title.Location = [System.Drawing.Point]::new(16, 12)
$title.Size = [System.Drawing.Size]::new(420, 30)
$form.Controls.Add($title)

$hint = [System.Windows.Forms.Label]::new()
$hint.Text = "Drag PDF files or folders here, then click Import."
$hint.Location = [System.Drawing.Point]::new(18, 48)
$hint.Size = [System.Drawing.Size]::new(520, 22)
$form.Controls.Add($hint)

$sourceList = [System.Windows.Forms.ListBox]::new()
$sourceList.Location = [System.Drawing.Point]::new(18, 78)
$sourceList.Size = [System.Drawing.Size]::new(560, 190)
$sourceList.Anchor = "Top,Left,Right"
$sourceList.AllowDrop = $true
$sourceList.HorizontalScrollbar = $true
$sourceList.Add_DragEnter({
    if ($_.Data.GetDataPresent([System.Windows.Forms.DataFormats]::FileDrop)) {
        $_.Effect = [System.Windows.Forms.DragDropEffects]::Copy
    }
})
$sourceList.Add_DragDrop({
    $paths = $_.Data.GetData([System.Windows.Forms.DataFormats]::FileDrop)
    foreach ($path in $paths) {
        Add-SourcePath $sourceList $path
    }
})
$form.Controls.Add($sourceList)

$addFilesButton = [System.Windows.Forms.Button]::new()
$addFilesButton.Text = "Add PDFs"
$addFilesButton.Location = [System.Drawing.Point]::new(600, 78)
$addFilesButton.Size = [System.Drawing.Size]::new(130, 32)
$addFilesButton.Anchor = "Top,Right"
$addFilesButton.Add_Click({
    $dialog = [System.Windows.Forms.OpenFileDialog]::new()
    $dialog.Filter = "PDF files (*.pdf)|*.pdf"
    $dialog.Multiselect = $true
    if ($dialog.ShowDialog() -eq [System.Windows.Forms.DialogResult]::OK) {
        foreach ($file in $dialog.FileNames) {
            Add-SourcePath $sourceList $file
        }
    }
})
$form.Controls.Add($addFilesButton)

$addFolderButton = [System.Windows.Forms.Button]::new()
$addFolderButton.Text = "Add Folder"
$addFolderButton.Location = [System.Drawing.Point]::new(600, 118)
$addFolderButton.Size = [System.Drawing.Size]::new(130, 32)
$addFolderButton.Anchor = "Top,Right"
$addFolderButton.Add_Click({
    $dialog = [System.Windows.Forms.FolderBrowserDialog]::new()
    if ($dialog.ShowDialog() -eq [System.Windows.Forms.DialogResult]::OK) {
        Add-SourcePath $sourceList $dialog.SelectedPath
    }
})
$form.Controls.Add($addFolderButton)

$removeButton = [System.Windows.Forms.Button]::new()
$removeButton.Text = "Remove"
$removeButton.Location = [System.Drawing.Point]::new(600, 158)
$removeButton.Size = [System.Drawing.Size]::new(130, 32)
$removeButton.Anchor = "Top,Right"
$removeButton.Add_Click({
    while ($sourceList.SelectedIndices.Count -gt 0) {
        $sourceList.Items.RemoveAt($sourceList.SelectedIndices[0])
    }
})
$form.Controls.Add($removeButton)

$clearButton = [System.Windows.Forms.Button]::new()
$clearButton.Text = "Clear"
$clearButton.Location = [System.Drawing.Point]::new(600, 198)
$clearButton.Size = [System.Drawing.Size]::new(130, 32)
$clearButton.Anchor = "Top,Right"
$clearButton.Add_Click({ $sourceList.Items.Clear() })
$form.Controls.Add($clearButton)

$categoryLabel = [System.Windows.Forms.Label]::new()
$categoryLabel.Text = "Category"
$categoryLabel.Location = [System.Drawing.Point]::new(18, 288)
$categoryLabel.Size = [System.Drawing.Size]::new(90, 24)
$form.Controls.Add($categoryLabel)

$categoryBox = [System.Windows.Forms.ComboBox]::new()
$categoryBox.Location = [System.Drawing.Point]::new(112, 284)
$categoryBox.Size = [System.Drawing.Size]::new(300, 28)
$categoryBox.DropDownStyle = [System.Windows.Forms.ComboBoxStyle]::DropDown
@(
    "New_Unclassified",
    "PU_Microphase_Separation",
    "TPU_Mechanics",
    "SAXS_WAXS_FTIR_DSC",
    "PCL_Based_Polyurethane",
    "Biodegradable_Polyurethane",
    "PVDF_Piezoelectric_Biomaterials",
    "ML_Polymer_Properties",
    "Self_Healing_Elastomer",
    "Shape_Memory_Polyurethane",
    "Ionogel_Magnetic_Ionogel",
    "Review_Background"
) | ForEach-Object { $categoryBox.Items.Add($_) | Out-Null }
$categoryBox.Text = "New_Unclassified"
$form.Controls.Add($categoryBox)

$maxPagesLabel = [System.Windows.Forms.Label]::new()
$maxPagesLabel.Text = "Max pages"
$maxPagesLabel.Location = [System.Drawing.Point]::new(440, 288)
$maxPagesLabel.Size = [System.Drawing.Size]::new(80, 24)
$form.Controls.Add($maxPagesLabel)

$maxPagesBox = [System.Windows.Forms.NumericUpDown]::new()
$maxPagesBox.Location = [System.Drawing.Point]::new(522, 284)
$maxPagesBox.Size = [System.Drawing.Size]::new(70, 28)
$maxPagesBox.Minimum = 1
$maxPagesBox.Maximum = 300
$maxPagesBox.Value = 30
$form.Controls.Add($maxPagesBox)

$noEvidenceCheck = [System.Windows.Forms.CheckBox]::new()
$noEvidenceCheck.Text = "Copy/extract only; do not add evidence"
$noEvidenceCheck.Location = [System.Drawing.Point]::new(18, 322)
$noEvidenceCheck.Size = [System.Drawing.Size]::new(280, 24)
$form.Controls.Add($noEvidenceCheck)

$restartCheck = [System.Windows.Forms.CheckBox]::new()
$restartCheck.Text = "Restart backend after import"
$restartCheck.Checked = $true
$restartCheck.Location = [System.Drawing.Point]::new(320, 322)
$restartCheck.Size = [System.Drawing.Size]::new(220, 24)
$form.Controls.Add($restartCheck)

$runButton = [System.Windows.Forms.Button]::new()
$runButton.Text = "Import and Update RAG"
$runButton.Location = [System.Drawing.Point]::new(600, 284)
$runButton.Size = [System.Drawing.Size]::new(190, 42)
$runButton.Anchor = "Top,Right"
$form.Controls.Add($runButton)

$logBox = [System.Windows.Forms.TextBox]::new()
$logBox.Location = [System.Drawing.Point]::new(18, 366)
$logBox.Size = [System.Drawing.Size]::new(860, 250)
$logBox.Anchor = "Top,Bottom,Left,Right"
$logBox.Multiline = $true
$logBox.ScrollBars = "Vertical"
$logBox.ReadOnly = $true
$logBox.WordWrap = $false
$logBox.Font = [System.Drawing.Font]::new("Consolas", 9)
$form.Controls.Add($logBox)

$runButton.Add_Click({
    if ($sourceList.Items.Count -eq 0) {
        [System.Windows.Forms.MessageBox]::Show("Add at least one PDF file or folder first.", "No input")
        return
    }

    $runButton.Enabled = $false
    $form.Cursor = [System.Windows.Forms.Cursors]::WaitCursor

    try {
        Append-Log $logBox "Project root: $ProjectRoot"
        $python = (Get-Command python).Source
        $powershell = (Get-Command powershell).Source

        foreach ($source in $sourceList.Items) {
            $args = @(
                "scripts\ingest_new_pdfs.py",
                "$source",
                "--category",
                $categoryBox.Text,
                "--max-pages",
                "$([int]$maxPagesBox.Value)"
            )
            if ($noEvidenceCheck.Checked) {
                $args += "--no-evidence"
            }
            Invoke-LoggedProcess -FilePath $python -Arguments $args -WorkingDirectory $ProjectRoot -LogBox $logBox
        }

        Invoke-LoggedProcess -FilePath $python -Arguments @("convert_to_json.py") -WorkingDirectory $ProjectRoot -LogBox $logBox

        if (-not $noEvidenceCheck.Checked) {
            Invoke-LoggedProcess -FilePath $powershell -Arguments @("-ExecutionPolicy", "Bypass", "-File", "scripts\rebuild_rag_index.ps1") -WorkingDirectory $ProjectRoot -LogBox $logBox
        }

        if ($restartCheck.Checked) {
            Invoke-LoggedProcess -FilePath $powershell -Arguments @("-ExecutionPolicy", "Bypass", "-File", "scripts\stop_backend.ps1") -WorkingDirectory $ProjectRoot -LogBox $logBox
            Invoke-LoggedProcess -FilePath $powershell -Arguments @("-ExecutionPolicy", "Bypass", "-File", "scripts\start_backend.ps1") -WorkingDirectory $ProjectRoot -LogBox $logBox
        }

        Append-Log $logBox "DONE."
        [System.Windows.Forms.MessageBox]::Show("Import finished.", "Academic-RAG")
    } catch {
        Append-Log $logBox "ERROR: $($_.Exception.Message)"
        [System.Windows.Forms.MessageBox]::Show($_.Exception.Message, "Import failed")
    } finally {
        $form.Cursor = [System.Windows.Forms.Cursors]::Default
        $runButton.Enabled = $true
    }
})

[void]$form.ShowDialog()
