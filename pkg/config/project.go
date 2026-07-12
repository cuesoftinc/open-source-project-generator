package config

import (
	"fmt"
	"os"
	"path/filepath"
	"strings"

	"github.com/cuesoftinc/open-source-project-generator/pkg/constants"
	"github.com/cuesoftinc/open-source-project-generator/pkg/mapper"
	"github.com/cuesoftinc/open-source-project-generator/pkg/models"
	"gopkg.in/yaml.v3"
)

type Components struct {
	Frontend any  `yaml:"frontend"` // bool (true for all apps) or []string (list of specific app names) in YAML
	Backend  bool `yaml:"backend"`
	Mobile   bool `yaml:"mobile"`
	Deploy   bool `yaml:"deploy"`
	Docs     bool `yaml:"docs"`
	Scripts  bool `yaml:"scripts"`
	Github   bool `yaml:"github"`
}

type ProjectConfig struct {
	ProjectName  string     `yaml:"project_name"`
	OutputFolder string     `yaml:"output_folder"`
	Components   Components `yaml:"components"`
}

type Project struct {
	ProjectName  string
	OutputFolder string
	Folders      []string
	Apps         models.Apps
}

func LoadProject(path string) (*Project, error) {
	// Clean the user-supplied path and reject any attempt to traverse to a
	// parent directory before opening the file (mitigates path inclusion).
	cleanPath := filepath.Clean(path)
	if cleanPath == ".." || strings.HasPrefix(cleanPath, ".."+string(os.PathSeparator)) {
		return nil, fmt.Errorf("invalid config file path %q: must not reference a parent directory", path)
	}

	data, err := os.ReadFile(cleanPath) // #nosec G304 -- path is cleaned and validated above to prevent directory traversal
	if err != nil {
		return nil, fmt.Errorf("failed to read config file: %w", err)
	}

	var cfg ProjectConfig
	if err := yaml.Unmarshal(data, &cfg); err != nil {
		return nil, fmt.Errorf("failed to parse config file: %w", err)
	}

	if err := validateProjectName(cfg.ProjectName); err != nil {
		return nil, err
	}

	project := &Project{
		ProjectName:  cfg.ProjectName,
		OutputFolder: cfg.OutputFolder,
		Folders:      []string{},
		Apps:         models.Apps{},
	}

	switch frontendValue := cfg.Components.Frontend.(type) {
	case []any:
		if len(frontendValue) > 0 {
			project.Folders = append(project.Folders, mapper.ComponentToFolder("frontend"))
			for _, app := range frontendValue {
				appStr, ok := app.(string)
				if !ok {
					return nil, fmt.Errorf("frontend apps must be strings, got %T", app)
				}
				project.Apps.Frontend = append(project.Apps.Frontend, appStr)
			}
		}
	case bool:
		if frontendValue {
			project.Folders = append(project.Folders, mapper.ComponentToFolder("frontend"))
			project.Apps.Frontend = constants.Apps.Frontend
		}
	}
	if cfg.Components.Backend {
		project.Folders = append(project.Folders, mapper.ComponentToFolder("backend"))
	}
	if cfg.Components.Mobile {
		project.Folders = append(project.Folders, mapper.ComponentToFolder("mobile"))
	}
	if cfg.Components.Deploy {
		project.Folders = append(project.Folders, mapper.ComponentToFolder("deploy"))
	}
	if cfg.Components.Docs {
		project.Folders = append(project.Folders, mapper.ComponentToFolder("docs"))
	}
	if cfg.Components.Scripts {
		project.Folders = append(project.Folders, mapper.ComponentToFolder("scripts"))
	}
	if cfg.Components.Github {
		project.Folders = append(project.Folders, mapper.ComponentToFolder("github"))
	}

	return project, nil
}

// validateProjectName ensures the configured project name is safe to use as a
// filesystem path segment and as an argument to external commands. It rejects
// empty names, parent-directory references, absolute paths, and embedded path
// separators.
func validateProjectName(name string) error {
	if name == "" {
		return fmt.Errorf("project_name must not be empty")
	}
	if strings.Contains(name, "..") {
		return fmt.Errorf("project_name %q must not contain '..'", name)
	}
	if filepath.IsAbs(name) {
		return fmt.Errorf("project_name %q must not be an absolute path", name)
	}
	if strings.ContainsAny(name, `/\`) {
		return fmt.Errorf("project_name %q must not contain path separators", name)
	}
	return nil
}
