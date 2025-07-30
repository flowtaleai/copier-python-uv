import pytest


def test_validate_author_name_valid(tmp_path, copier):
    custom_answers = {"author_name": "test user"}
    copier.copy(tmp_path, **custom_answers)


@pytest.mark.parametrize(
    "author_name",
    ["A", "", " "],
)
def test_validate_author_name_invalid(tmp_path, copier, author_name):
    custom_answers = {"author_name": "test user"}
    copier.copy(tmp_path, **custom_answers)


@pytest.mark.parametrize(
    "distribution_name",
    [
        "validpackagename",
        "valid_package_name",
        "valid-package-name",
        "valid.distribution.name",
        "valid.distribution.package_name",
        "valid_distribution.package_name",
        "long-but-valid-distribution-name",
    ],
)
def test_validate_distribution_name_valid(tmp_path, copier, distribution_name):
    custom_answers = {"distribution_name": distribution_name}
    copier.copy(tmp_path, **custom_answers)


@pytest.mark.parametrize(
    "distribution_name",
    [
        "",
        "-test",
        "test-",
        "distribution name",
        ".distribution.name",
        "distribution.name.",
        "invalid.distribution.package.name",
        "distribution..name",
        "distribution-name_",
        "_distribution-name",
        "distribution--name",
    ],
)
def test_validate_distribution_name_invalid(tmp_path, copier, distribution_name):
    custom_answers = {"distribution_name": distribution_name}
    with pytest.raises(
        ValueError,
        match="distribution name must start with a lowercase letter and can",
    ):
        copier.copy(tmp_path, **custom_answers)


@pytest.mark.parametrize(
    "package_name",
    [
        "validpackagename",
        "valid_package_name",
        "valid_package_name_",
        "another.valid.packagename",
        "my_other.valid.package_name",
    ],
)
def test_validate_package_name_valid(tmp_path, copier, package_name):
    custom_answers = {"package_name": package_name}
    copier.copy(tmp_path, **custom_answers)


@pytest.mark.parametrize(
    "package_name",
    [
        "invalid-package-name",
        "2invalidpackagename",
        "invalidPackageName",
        "_invalidpackagename",
        "invalid/package/name",
        "another.invalid.package.name",
        "this is bad",
    ],
)
def test_validate_package_name_invalid(tmp_path, copier, package_name):
    custom_answers = {"package_name": package_name}
    with pytest.raises(
        ValueError,
        match="package name must start with a lowercase letter",
    ):
        copier.copy(tmp_path, **custom_answers)


@pytest.mark.parametrize("email", ["1@1.2", "test@test.com"])
def test_validate_email_valid(tmp_path, copier, email):
    custom_answers = {"author_email": email}
    copier.copy(tmp_path, **custom_answers)


@pytest.mark.parametrize("email", ["", " ", "test@test", "test.com"])
def test_validate_email_invalid(tmp_path, copier, email):
    custom_answers = {"author_email": email}
    with pytest.raises(
        ValueError,
        match="Author email must be a valid email address",
    ):
        copier.copy(tmp_path, **custom_answers)


@pytest.mark.parametrize("version", ["0.1.0", "1.2.3", "10.20.30"])
def test_validate_version_valid(tmp_path, copier, version):
    custom_answers = {"version": version}
    copier.copy(tmp_path, **custom_answers)


@pytest.mark.parametrize("version", ["invalid_version", "1.2.3.4.5.6.a"])
def test_validate_version_invalid(tmp_path, copier, version):
    custom_answers = {"version": version}
    with pytest.raises(
        ValueError,
        match="Version must be in the format of 'MAJOR.MINOR.PATCH'",
    ):
        copier.copy(tmp_path, **custom_answers)


@pytest.mark.parametrize("uv_version", ["0.7.11", "0.7.13"])
def test_validate_uv_version_valid(tmp_path, copier, uv_version):
    custom_answers = {"uv_version": uv_version}
    copier.copy(tmp_path, **custom_answers)


@pytest.mark.parametrize("uv_version", ["", "1.0.0.1.1", "invalid_version"])
def test_validate_uv_version_invalid(tmp_path, copier, uv_version):
    custom_answers = {"uv_version": uv_version}
    with pytest.raises(ValueError, match="uv version must follow semantic versioning"):
        copier.copy(tmp_path, **custom_answers)
