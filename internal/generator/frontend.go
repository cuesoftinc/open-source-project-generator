package generator

import (
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"regexp"

	"github.com/cuesoftinc/open-source-project-generator/pkg/output"
)

// validAppName restricts generated app names to lowercase letters, digits, and
// hyphens. This matches npm package naming rules and prevents command injection
// via untrusted values passed to the "npx" subprocess.
var validAppName = regexp.MustCompile(`^[a-z0-9-]+$`)

type FrontendGenerator struct {
	Version    string
	ProjectDir string
	Component  string
	Apps       []string
}

func (g *FrontendGenerator) Generate(projectName string) error {
	appPath := filepath.Join(g.ProjectDir, g.Component)

	for _, app := range g.Apps {
		appName := projectName + "-" + app
		if !validAppName.MatchString(appName) {
			return fmt.Errorf("invalid app name %q: must match %s", appName, `^[a-z0-9-]+$`)
		}

		// #nosec G204 -- appName is validated against ^[a-z0-9-]+$ above; the command and all remaining arguments are static literals
		cmd := exec.Command("npx", fmt.Sprintf("create-next-app@%s", g.Version), appName,
			"--typescript",
			"--tailwind",
			"--app",
			"--disable-git",
			"--eslint",
			"--turbopack",
			"--src-dir",
			"--import-alias", "@/*",
			"--react-compiler",
			"--skip-install")
		cmd.Dir = appPath
		cmd.Stderr = os.Stderr

		spinner := output.NewSpinner(fmt.Sprintf("Setting up %s app...", app))
		spinner.Start()

		err := cmd.Run()
		spinner.Stop()

		if err != nil {
			return fmt.Errorf("failed to create %s app: %w", app, err)
		}

		oldPath := filepath.Join(appPath, appName)
		newPath := filepath.Join(appPath, app)
		if err := os.Rename(oldPath, newPath); err != nil {
			return fmt.Errorf("failed to rename %s folder: %w", app, err)
		}

		fmt.Printf(output.ColorGreen+"✔"+output.ColorReset+" Done setting up %s app\n", app)
	}

	return nil
}
